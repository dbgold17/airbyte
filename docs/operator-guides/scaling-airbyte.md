---
products: oss-*
---

# Scaling Airbyte

As depicted in our [High-Level View](../understanding-airbyte/high-level-view.md), Airbyte is made up of several components under the hood: 1. Scheduler 2. Server 3. Temporal 4. Webapp 5. Database

These components perform control plane operations that are low-scale, low-resource work. In addition to the work being low cost, these components are efficient and optimized for these jobs, meaning that only uncommonly large workloads will require deployments at scale. In general, you would only encounter scaling issues when running over a thousand connections.

As a reference point, the typical Airbyte user has 5 - 20 connectors and 10 - 100 connections configured. Almost all of these connections are scheduled, either hourly or daily, resulting in at most 100 concurrent jobs.

## What To Scale

[Workloads](../understanding-airbyte/jobs.md) do all the heavy lifting within Airbyte. The workload system is responsible for launching the pods that execute Airbyte operations \(e.g. Discover, Read, Sync etc\).

The workload launcher will create one Kubernetes pod. The connector and sidecar images then do all the actual work.

Thus, scaling Airbyte is a matter of ensuring that the Kubernetes cluster Airbyte runs on has sufficient resources to schedule its various job pods.

Jobs-wise, we are mainly concerned with Sync jobs when thinking about scale. Sync jobs sync data from sources to destinations and are the majority of jobs run. Sync jobs use two workers. One worker reads from the source; the other worker writes to the destination.

**In general, we recommend starting out with a mid-sized cloud instance \(e.g. 4 or 8 cores\) and gradually tuning instance size to your workload.**

There are two resources to be aware of when thinking of scale: 1. Memory 2. Disk space

### Memory

As mentioned above, we are mainly concerned with scaling Sync jobs. Within a Sync job, the main memory culprit is the Source worker.

This is because the Source worker reads up to 10,000 records in memory. This can present problems for database sources with tables that have large row sizes. e.g. a table with an average row size of 0.5MBs will require 0.5 \* 10000 / 1000 = 5GBs of RAM. See [this issue](https://github.com/airbytehq/airbyte/issues/3439) for more information.

There are several ways to increase available memory for syncs. See [Configuring connector resources](configuring-connector-resources) for details.

### Disk Space

Airbyte uses backpressure to try to read the minimal amount of logs required. In the past, disk space was a large concern, but we've since deprecated the expensive on-disk queue approach.

However, disk space might become an issue for the following reasons:

1. Long-running syncs can produce a fair amount of logs. Some work has been done to minimize accidental logging, so this should no longer be an acute problem, but is still an open issue.
2. Although Airbyte connector images aren't massive, they aren't exactly small either. The typical connector image is ~300MB. An Airbyte deployment with multiple connectors can easily use up to 10GBs of disk space.

Because of this, we recommend allocating a minimum of 30GBs of disk space per node. Since storage is on the cheaper side, we'd recommend you be safe than sorry, so err on the side of over-provisioning.

### On Kubernetes

Users running Airbyte Kubernetes also have to make sure the Kubernetes cluster can accommodate the number of pods Airbyte creates.

To be safe, make sure the Kubernetes cluster can schedule up to `2 x <number-of-possible-concurrent-connections>` pods at once. This is the worse case estimate, and most users should be fine with `2 x <number-of-possible-concurrent-connections>` as a rule of thumb.

### Temporal DB

Temporal maintains multiple idle connections. By the default value is `20` and you may want to lower or increase this number. One issue we noticed is
that temporal creates multiple pools and the number specified in the `SQL_MAX_IDLE_CONNS` environment variable and
might end up allowing 4-5 times more connections than expected.

If you want to increase the amount of allowed idle connections, you will also need to increase `SQL_MAX_CONNS` as well because `SQL_MAX_IDLE_CONNS`
is capped by `SQL_MAX_CONNS`.

## Feedback

The advice here is best-effort and by no means comprehensive. Please reach out on Slack if anything doesn't make sense or if something can be improved.

If you've been running Airbyte in production and have more tips up your sleeve, we welcome contributions!
