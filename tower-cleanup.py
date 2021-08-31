#! /usr/bin/python3

# This script cleans up all Batch queues and compute environments
# It also removes all ECS clusters except for the tower cluster
#
# TODO: Instead of the approach describel above, we should call
# the Nextflow Tower API to delete a particular tower compute environment for it
# then make calls to remove particular queues, batch compute environments,
# clusters, and role

import boto3
import time

DISABLED = 'DISABLED'
TOWER_CLUSTER = 'nf-tower'
batch = boto3.client('batch')
ecs = boto3.client('ecs')

batch_job_queue_arns = [
  queue['jobQueueArn']
  for queue in batch.describe_job_queues()['jobQueues']
]
batch_compute_env_arns = [
  env['computeEnvironmentArn']
  for env in batch.describe_compute_environments()['computeEnvironments']
]
ecs_cluster_arns = list(
  filter(
    lambda arn: TOWER_CLUSTER not in arn,
    ecs.list_clusters()['clusterArns']
    )
  )

# disable queues
for arn in batch_job_queue_arns:
  batch.update_job_queue(jobQueue=arn, state=DISABLED)

# disable environments
for arn in batch_compute_env_arns:
  batch.update_compute_environment(computeEnvironment=arn, state=DISABLED)

# wait a short time -- a waiter would be better, but batch has none
time.sleep(15)

# delete queues
for arn in batch_job_queue_arns:
  batch.delete_job_queue(jobQueue=arn)

# wait a short time before attempting to remove environments
time.sleep(15)

# delete environments
for arn in batch_compute_env_arns:
  batch.delete_compute_environment(computeEnvironment=arn)

# delete clusters
for arn in ecs_cluster_arns:
  ecs.delete_cluster(cluster=arn)
