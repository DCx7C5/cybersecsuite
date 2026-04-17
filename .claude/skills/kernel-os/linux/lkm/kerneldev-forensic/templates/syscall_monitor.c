// SPDX-License-Identifier: GPL-2.0
/*
 * Forensic Syscall Monitor Template
 *
 * Advanced syscall interception and monitoring for APT detection
 * and forensic investigation. Designed for integration with the
 * CyberSec forensic framework.
 *
 * Features:
 * - Selective syscall monitoring (configurable)
 * - Process filtering by PID/PPID/command
 * - Real-time logging to ring buffer
 * - Integration with IOC detection
 * - MITRE ATT&CK technique mapping
 *
 * Sysfs Interface: /sys/kernel/syscall_monitor/
 * - config: Monitoring configuration
 * - filters: Process and syscall filters
 * - log: Recent syscall events
 * - stats: Monitoring statistics
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/kprobes.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/ring_buffer.h>
#include <linux/time.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("CyberSec Forensic Framework");
MODULE_DESCRIPTION("Advanced syscall monitoring for APT detection");
MODULE_VERSION("1.0");

/* Configuration */
static bool monitoring_enabled = false;
static bool log_all_syscalls = false;
static bool filter_by_process = true;
static char monitored_processes[512] = "bash,sh,python,python3,nc,netcat,curl,wget";
static char monitored_syscalls[512] = "execve,execveat,ptrace,kill,tkill,tgkill,mmap,mprotect,socket,connect,bind,listen,accept,open,openat,read,write";

/* Statistics */
static unsigned long total_syscalls = 0;
static unsigned long filtered_syscalls = 0;
static unsigned long suspicious_syscalls = 0;

/* Ring buffer for syscall events */
static struct ring_buffer *syscall_rb;
static struct ring_buffer_event *rb_event;

/* Sysfs objects */
static struct kobject *monitor_kobj;

/* Syscall event structure */
struct syscall_event {
    unsigned long timestamp;
    pid_t pid;
    pid_t ppid;
    uid_t uid;
    char comm[TASK_COMM_LEN];
    unsigned long syscall_nr;
    unsigned long args[6];
    char mitre_technique[16];  // e.g., T1055, T1134
};

/*
 * Utility functions
 */
static bool is_monitored_process(const char *comm)
{
    char *pos, *process_list, *process_name;
    bool found = false;

    if (!filter_by_process)
        return true;

    process_list = kstrdup(monitored_processes, GFP_KERNEL);
    if (!process_list)
        return false;

    pos = process_list;
    while ((process_name = strsep(&pos, ",")) != NULL) {
        if (strcmp(comm, process_name) == 0) {
            found = true;
            break;
        }
    }

    kfree(process_list);
    return found;
}

static bool is_monitored_syscall(unsigned long syscall_nr)
{
    /* Common suspicious syscalls for APT techniques */
    switch (syscall_nr) {
        case __NR_execve:          // T1059 - Command execution
        case __NR_execveat:        // T1059 - Command execution
        case __NR_ptrace:          // T1055 - Process injection
        case __NR_kill:            // T1562 - Process termination
        case __NR_tkill:           // T1562 - Process termination
        case __NR_tgkill:          // T1562 - Process termination
        case __NR_mmap:            // T1055 - Memory mapping
        case __NR_mprotect:        // T1055 - Memory protection
        case __NR_socket:          // T1095 - Network connections
        case __NR_connect:         // T1095 - Network connections
        case __NR_bind:            // T1095 - Network binding
        case __NR_listen:          // T1095 - Network listening
        case __NR_accept:          // T1095 - Network accept
        case __NR_open:            // T1005 - File access
        case __NR_openat:          // T1005 - File access
            return true;
        default:
            return log_all_syscalls;
    }
}

static const char* get_mitre_technique(unsigned long syscall_nr)
{
    switch (syscall_nr) {
        case __NR_execve:
        case __NR_execveat:
            return "T1059";  // Command and Scripting Interpreter
        case __NR_ptrace:
        case __NR_mmap:
        case __NR_mprotect:
            return "T1055";  // Process Injection
        case __NR_kill:
        case __NR_tkill:
        case __NR_tgkill:
            return "T1562";  // Impair Defenses
        case __NR_socket:
        case __NR_connect:
        case __NR_bind:
        case __NR_listen:
        case __NR_accept:
            return "T1095";  // Non-Application Layer Protocol
        case __NR_open:
        case __NR_openat:
            return "T1005";  // Data from Local System
        default:
            return "UNKNOWN";
    }
}

/*
 * Syscall interception using kprobe
 */
static int syscall_entry_handler(struct kretprobe_instance *ri, struct pt_regs *regs)
{
    struct syscall_event event;
    struct task_struct *task = current;
    struct timespec64 ts;

    if (!monitoring_enabled)
        return 0;

    total_syscalls++;

    /* Check if we should monitor this process */
    if (!is_monitored_process(task->comm)) {
        filtered_syscalls++;
        return 0;
    }

    /* Check if we should monitor this syscall */
    unsigned long syscall_nr = regs->orig_ax;  // x86_64 specific
    if (!is_monitored_syscall(syscall_nr)) {
        filtered_syscalls++;
        return 0;
    }

    /* Log suspicious syscall patterns */
    if (syscall_nr == __NR_ptrace || syscall_nr == __NR_mprotect) {
        suspicious_syscalls++;
        pr_warn("syscall_monitor: Suspicious syscall %lu from %s[%d]\n",
                syscall_nr, task->comm, task->pid);
    }

    /* Create event record */
    ktime_get_real_ts64(&ts);
    event.timestamp = (unsigned long)(ts.tv_sec * 1000000 + ts.tv_nsec / 1000);
    event.pid = task->pid;
    event.ppid = task->real_parent->pid;
    event.uid = from_kuid_munged(current_user_ns(), task_uid(task));
    strncpy(event.comm, task->comm, TASK_COMM_LEN - 1);
    event.comm[TASK_COMM_LEN - 1] = '\0';
    event.syscall_nr = syscall_nr;

    /* Copy syscall arguments */
    event.args[0] = regs->di;  // x86_64 specific
    event.args[1] = regs->si;
    event.args[2] = regs->dx;
    event.args[3] = regs->r10;
    event.args[4] = regs->r8;
    event.args[5] = regs->r9;

    strncpy(event.mitre_technique, get_mitre_technique(syscall_nr), 15);
    event.mitre_technique[15] = '\0';

    /* Store in ring buffer */
    rb_event = ring_buffer_lock_reserve(syscall_rb, sizeof(event));
    if (rb_event) {
        memcpy(ring_buffer_event_data(rb_event), &event, sizeof(event));
        ring_buffer_unlock_commit(syscall_rb, rb_event);
    }

    return 0;
}

/* Kretprobe for syscall monitoring */
static struct kretprobe syscall_kretprobe = {
    .handler = syscall_entry_handler,
    .maxactive = 100,
    .kp.symbol_name = "sys_call_table",  // This needs proper implementation
};

/*
 * Sysfs interface
 */
static ssize_t config_show(struct kobject *kobj, struct kobj_attribute *attr,
                          char *buf)
{
    return sprintf(buf,
        "monitoring_enabled=%s\n"
        "log_all_syscalls=%s\n"
        "filter_by_process=%s\n"
        "monitored_processes=%s\n"
        "monitored_syscalls=%s\n",
        monitoring_enabled ? "true" : "false",
        log_all_syscalls ? "true" : "false",
        filter_by_process ? "true" : "false",
        monitored_processes,
        monitored_syscalls);
}

static ssize_t config_store(struct kobject *kobj, struct kobj_attribute *attr,
                           const char *buf, size_t count)
{
    char *config_copy, *config_iter, *line, *key, *value;

    config_copy = kstrdup(buf, GFP_KERNEL);
    if (!config_copy)
        return -ENOMEM;

    config_iter = config_copy;

    while ((line = strsep(&config_iter, "\n")) != NULL) {
        key = strsep(&line, "=");
        value = line;

        if (!key || !value)
            continue;

        if (strcmp(key, "monitoring_enabled") == 0) {
            monitoring_enabled = (strcmp(value, "true") == 0);
        } else if (strcmp(key, "log_all_syscalls") == 0) {
            log_all_syscalls = (strcmp(value, "true") == 0);
        } else if (strcmp(key, "filter_by_process") == 0) {
            filter_by_process = (strcmp(value, "true") == 0);
        } else if (strcmp(key, "monitored_processes") == 0) {
            strncpy(monitored_processes, value, sizeof(monitored_processes) - 1);
            monitored_processes[sizeof(monitored_processes) - 1] = '\0';
        } else if (strcmp(key, "monitored_syscalls") == 0) {
            strncpy(monitored_syscalls, value, sizeof(monitored_syscalls) - 1);
            monitored_syscalls[sizeof(monitored_syscalls) - 1] = '\0';
        }
    }

    kfree(config_copy);
    pr_info("syscall_monitor: configuration updated\n");
    return count;
}

static ssize_t stats_show(struct kobject *kobj, struct kobj_attribute *attr,
                         char *buf)
{
    return sprintf(buf,
        "total_syscalls=%lu\n"
        "filtered_syscalls=%lu\n"
        "monitored_syscalls=%lu\n"
        "suspicious_syscalls=%lu\n"
        "monitoring_enabled=%s\n"
        "ring_buffer_size=%lu\n",
        total_syscalls,
        filtered_syscalls,
        total_syscalls - filtered_syscalls,
        suspicious_syscalls,
        monitoring_enabled ? "true" : "false",
        ring_buffer_size(syscall_rb));
}

static ssize_t log_show(struct kobject *kobj, struct kobj_attribute *attr,
                       char *buf)
{
    struct ring_buffer_iter *iter;
    struct ring_buffer_event *event;
    struct syscall_event *syscall_ev;
    int pos = 0;
    int count = 0;
    const int max_events = 10;  // Show last 10 events

    iter = ring_buffer_read_prepare(syscall_rb, 0);
    if (!iter)
        return sprintf(buf, "Error reading ring buffer\n");

    ring_buffer_read_start(iter);

    while ((event = ring_buffer_read(iter, NULL)) != NULL && count < max_events) {
        syscall_ev = ring_buffer_event_data(event);
        pos += snprintf(buf + pos, PAGE_SIZE - pos,
            "%lu: %s[%d] syscall=%lu technique=%s uid=%u args=%lx,%lx,%lx\n",
            syscall_ev->timestamp,
            syscall_ev->comm,
            syscall_ev->pid,
            syscall_ev->syscall_nr,
            syscall_ev->mitre_technique,
            syscall_ev->uid,
            syscall_ev->args[0],
            syscall_ev->args[1],
            syscall_ev->args[2]);
        count++;
    }

    ring_buffer_read_finish(iter);

    if (pos == 0)
        pos = sprintf(buf, "No syscall events logged\n");

    return pos;
}

/* Define attributes */
static struct kobj_attribute config_attribute =
    __ATTR(config, 0664, config_show, config_store);

static struct kobj_attribute stats_attribute =
    __ATTR_RO(stats);

static struct kobj_attribute log_attribute =
    __ATTR_RO(log);

static struct attribute *attrs[] = {
    &config_attribute.attr,
    &stats_attribute.attr,
    &log_attribute.attr,
    NULL,
};

static struct attribute_group attr_group = {
    .attrs = attrs,
};

static int __init syscall_monitor_init(void)
{
    int retval;

    /* Create ring buffer for syscall events */
    syscall_rb = ring_buffer_alloc(1024 * 1024, RB_FL_OVERWRITE);
    if (!syscall_rb) {
        pr_err("syscall_monitor: failed to allocate ring buffer\n");
        return -ENOMEM;
    }

    /* Create sysfs interface */
    monitor_kobj = kobject_create_and_add("syscall_monitor", kernel_kobj);
    if (!monitor_kobj) {
        pr_err("syscall_monitor: failed to create kobject\n");
        ring_buffer_free(syscall_rb);
        return -ENOMEM;
    }

    retval = sysfs_create_group(monitor_kobj, &attr_group);
    if (retval) {
        pr_err("syscall_monitor: failed to create sysfs group\n");
        kobject_put(monitor_kobj);
        ring_buffer_free(syscall_rb);
        return retval;
    }

    /* Note: Actual syscall interception would require more complex kprobe setup
     * or ftrace integration. This is a template showing the structure. */

    pr_info("syscall_monitor: module loaded successfully\n");
    pr_info("syscall_monitor: interface at /sys/kernel/syscall_monitor/\n");
    pr_info("syscall_monitor: configure with echo 'monitoring_enabled=true' > /sys/kernel/syscall_monitor/config\n");

    return 0;
}

static void __exit syscall_monitor_exit(void)
{
    monitoring_enabled = false;

    /* Cleanup would include unregistering kprobes here */

    if (monitor_kobj) {
        kobject_put(monitor_kobj);
    }

    if (syscall_rb) {
        ring_buffer_free(syscall_rb);
    }

    pr_info("syscall_monitor: module unloaded, %lu syscalls monitored\n",
            total_syscalls - filtered_syscalls);
}

module_init(syscall_monitor_init);
module_exit(syscall_monitor_exit);