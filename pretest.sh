#!/bin/sh
# http://blog.mellenthin.de/archives/2010/10/18/gdb-attach-fails-with-ptrace-operation-not-permitted/
echo "ptrace_scope: $(cat /proc/sys/kernel/yama/ptrace_scope)"
echo 0 > /proc/sys/kernel/yama/ptrace_scope
echo "ptrace_scope: $(cat /proc/sys/kernel/yama/ptrace_scope)"
