// SPDX-License-Identifier: GPL-2.0
/*
 * Forensic Sysfs Interface Template
 *
 * Creates a clean, modern sysfs interface for forensic data exchange:
 *   /sys/kernel/forensic_mcp/
 *
 * Files created:
 *   - message     (rw) : Command/response interface for forensic tools
 *   - status      (ro) : Module status, statistics, and health
 *   - alerts      (ro) : Real-time threat alerts and findings
 *   - config      (rw) : Runtime configuration for monitoring
 *   - iocs        (rw) : IOC submission and retrieval interface
 *
 * Designed for integration with CyberSec forensic framework and
 * kerneldev-mcp development workflow.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/utsname.h>
#include <linux/jiffies.h>
#include <linux/time.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("CyberSec Forensic Framework");
MODULE_DESCRIPTION("Forensic sysfs interface for kernel ↔ userspace communication");
MODULE_VERSION("1.0");

static struct kobject *forensic_kobj;

// Communication buffers
static char command_buffer[1024] = "READY\n";
static char response_buffer[2048] = "";
static char alert_buffer[4096] = "";
static char config_buffer[512] = "monitor_level=medium\nlog_syscalls=false\nreal_time_alerts=true\n";
static char ioc_buffer[2048] = "";

// Statistics and state
static unsigned int command_count = 0;
static unsigned int alert_count = 0;
static unsigned long module_start_time;
static bool monitoring_active = false;

/*
 * Message Interface - Command/Response for forensic tools
 */
static ssize_t message_show(struct kobject *kobj, struct kobj_attribute *attr,
                           char *buf)
{
    return sprintf(buf, "%s", response_buffer[0] ? response_buffer : "OK\n");
}

static ssize_t message_store(struct kobject *kobj, struct kobj_attribute *attr,
                            const char *buf, size_t count)
{
    size_t len = min(count, sizeof(command_buffer) - 1);
    strncpy(command_buffer, buf, len);
    command_buffer[len] = '\0';

    /* Remove trailing newline */
    if (len > 0 && command_buffer[len - 1] == '\n')
        command_buffer[len - 1] = '\0';

    command_count++;

    /* Process forensic commands */
    if (strncmp(command_buffer, "START_MONITOR", 13) == 0) {
        monitoring_active = true;
        strcpy(response_buffer, "MONITORING_STARTED\n");
        pr_info("forensic_mcp: monitoring started\n");
    } else if (strncmp(command_buffer, "STOP_MONITOR", 12) == 0) {
        monitoring_active = false;
        strcpy(response_buffer, "MONITORING_STOPPED\n");
        pr_info("forensic_mcp: monitoring stopped\n");
    } else if (strncmp(command_buffer, "GET_STATS", 9) == 0) {
        snprintf(response_buffer, sizeof(response_buffer),
                 "commands=%u,alerts=%u,uptime=%lu,monitoring=%s\n",
                 command_count, alert_count,
                 (unsigned long)(jiffies - module_start_time) / HZ,
                 monitoring_active ? "active" : "inactive");
    } else if (strncmp(command_buffer, "PING", 4) == 0) {
        strcpy(response_buffer, "PONG\n");
    } else {
        strcpy(response_buffer, "UNKNOWN_COMMAND\n");
    }

    return count;
}

/*
 * Status Interface - Module health and statistics
 */
static ssize_t status_show(struct kobject *kobj, struct kobj_attribute *attr,
                          char *buf)
{
    unsigned long uptime_sec = (jiffies - module_start_time) / HZ;
    struct timespec64 ts;
    ktime_get_real_ts64(&ts);

    return sprintf(buf,
        "module: forensic_mcp\n"
        "version: 1.0\n"
        "status: %s\n"
        "uptime: %lu seconds\n"
        "commands_processed: %u\n"
        "alerts_generated: %u\n"
        "monitoring_active: %s\n"
        "timestamp: %lld.%09ld\n"
        "kernel: %s\n",
        "operational",
        uptime_sec,
        command_count,
        alert_count,
        monitoring_active ? "yes" : "no",
        (long long)ts.tv_sec, ts.tv_nsec,
        UTS_RELEASE);
}

/*
 * Alerts Interface - Real-time threat alerts and findings
 */
static ssize_t alerts_show(struct kobject *kobj, struct kobj_attribute *attr,
                          char *buf)
{
    if (!alert_buffer[0]) {
        return sprintf(buf, "No active alerts\n");
    }
    return sprintf(buf, "%s", alert_buffer);
}

static ssize_t alerts_store(struct kobject *kobj, struct kobj_attribute *attr,
                           const char *buf, size_t count)
{
    size_t len = min(count, sizeof(alert_buffer) - 1);
    struct timespec64 ts;
    ktime_get_real_ts64(&ts);

    /* Add timestamp and store alert */
    snprintf(alert_buffer, sizeof(alert_buffer),
             "[%lld.%09ld] %.*s",
             (long long)ts.tv_sec, ts.tv_nsec, (int)len, buf);

    alert_count++;
    pr_warn("forensic_mcp: ALERT: %.*s", (int)len, buf);
    return count;
}

/*
 * Configuration Interface - Runtime configuration
 */
static ssize_t config_show(struct kobject *kobj, struct kobj_attribute *attr,
                          char *buf)
{
    return sprintf(buf, "%s", config_buffer);
}

static ssize_t config_store(struct kobject *kobj, struct kobj_attribute *attr,
                           const char *buf, size_t count)
{
    size_t len = min(count, sizeof(config_buffer) - 1);
    strncpy(config_buffer, buf, len);
    config_buffer[len] = '\0';

    pr_info("forensic_mcp: configuration updated\n");
    return count;
}

/*
 * IOC Interface - Indicator of Compromise management
 */
static ssize_t iocs_show(struct kobject *kobj, struct kobj_attribute *attr,
                        char *buf)
{
    return sprintf(buf, "%s", ioc_buffer[0] ? ioc_buffer : "No IOCs loaded\n");
}

static ssize_t iocs_store(struct kobject *kobj, struct kobj_attribute *attr,
                         const char *buf, size_t count)
{
    size_t len = min(count, sizeof(ioc_buffer) - 1);
    strncpy(ioc_buffer, buf, len);
    ioc_buffer[len] = '\0';

    pr_info("forensic_mcp: IOCs updated\n");
    return count;
}

/* Define attributes */
static struct kobj_attribute message_attribute =
    __ATTR(message, 0664, message_show, message_store);

static struct kobj_attribute status_attribute =
    __ATTR_RO(status);

static struct kobj_attribute alerts_attribute =
    __ATTR(alerts, 0664, alerts_show, alerts_store);

static struct kobj_attribute config_attribute =
    __ATTR(config, 0664, config_show, config_store);

static struct kobj_attribute iocs_attribute =
    __ATTR(iocs, 0664, iocs_show, iocs_store);

/* Group of attributes */
static struct attribute *attrs[] = {
    &message_attribute.attr,
    &status_attribute.attr,
    &alerts_attribute.attr,
    &config_attribute.attr,
    &iocs_attribute.attr,
    NULL,
};

static struct attribute_group attr_group = {
    .attrs = attrs,
};

static int __init forensic_mcp_init(void)
{
    int retval;

    /* Record start time */
    module_start_time = jiffies;

    /* Create /sys/kernel/forensic_mcp/ */
    forensic_kobj = kobject_create_and_add("forensic_mcp", kernel_kobj);
    if (!forensic_kobj) {
        pr_err("forensic_mcp: failed to create kobject\n");
        return -ENOMEM;
    }

    /* Create the files */
    retval = sysfs_create_group(forensic_kobj, &attr_group);
    if (retval) {
        pr_err("forensic_mcp: failed to create sysfs group\n");
        kobject_put(forensic_kobj);
        return retval;
    }

    /* Initialize response buffer */
    strcpy(response_buffer, "FORENSIC_MODULE_READY\n");

    pr_info("forensic_mcp: successfully created /sys/kernel/forensic_mcp/\n");
    pr_info("forensic_mcp: interface ready for forensic communication\n");
    pr_info("forensic_mcp: try: echo 'PING' > /sys/kernel/forensic_mcp/message\n");
    pr_info("forensic_mcp: try: cat /sys/kernel/forensic_mcp/status\n");

    return 0;
}

static void __exit forensic_mcp_exit(void)
{
    if (forensic_kobj) {
        kobject_put(forensic_kobj);
        pr_info("forensic_mcp: sysfs interface removed\n");
        pr_info("forensic_mcp: module unloaded after processing %u commands\n", command_count);
    }
}

module_init(forensic_mcp_init);
module_exit(forensic_mcp_exit);