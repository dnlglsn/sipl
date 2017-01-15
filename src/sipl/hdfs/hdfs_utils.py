from subprocess import call
import os


def hdfs_rm(path):
    call(["hdfs", "dfs", "-rm", "-f", os.path.join(path, "*")])
    call(["hdfs", "dfs", "-rmdir", path])


def hdfs_rmdir(path):
    call(["hdfs", "dfs", "-rmdir", path])


def hdfs_exists(path):
    return not call(["hdfs", "dfs", "-ls", path])


def hdfs_ls(path="hdfs://localhost:9000/*"):
    return call(["hdfs", "dfs", "-ls", path])
