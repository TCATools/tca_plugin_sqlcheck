#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys
import json
import fnmatch
import argparse
import subprocess

import settings


class SQLCheck(object):
    @staticmethod
    def init_env():
        tool_dir = settings.TOOL_DIR
        os.environ["SQLCHECK_HOME"] = os.path.join(tool_dir, settings.PLATFORMS[sys.platform], "sqlcheck-x86_64")
        os.environ["PATH"] = os.pathsep.join(
            [
                os.path.join(os.environ["SQLCHECK_HOME"], "bin"),
                os.environ["PATH"],
            ]
        )

    def __parse_args(self):
        """
        解析命令
        :return:
        """
        argparser = argparse.ArgumentParser()
        subparsers = argparser.add_subparsers(dest="command", help="Commands", required=True)
        # 检查在当前机器环境是否可用
        subparsers.add_parser("check", help="检查在当前机器环境是否可用")
        # 执行代码扫描
        subparsers.add_parser("scan", help="执行代码扫描")
        return argparser.parse_args()

    def __get_task_params(self):
        """
        获取需要任务参数
        :return:
        """
        task_request_file = os.environ.get("TASK_REQUEST")

        with open(task_request_file, "r") as rf:
            task_request = json.load(rf)

        task_params = task_request["task_params"]

        return task_params

    def __get_dir_files(self, root_dir, want_suffix=""):
        """
        在指定的目录下,递归获取符合后缀名要求的所有文件
        :param root_dir:
        :param want_suffix:
                    str|tuple,文件后缀名.单个直接传,比如 ".py";多个以元组形式,比如 (".h", ".c", ".cpp")
                    默认为空字符串,会匹配所有文件
        :return: list, 文件路径列表
        """
        files = set()
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                if f.lower().endswith(want_suffix):
                    fullpath = os.path.join(dirpath, f)
                    files.add(fullpath)
        files = list(files)
        return files

    def __format_str(self, text):
        """
        格式化字符串
        :param text:
        :return:
        """
        text = text.strip()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return text.strip("'\"")

    def __run_cmd(self, cmd_args):
        """
        执行命令行
        """
        print("[run cmd] %s" % " ".join(cmd_args))
        p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        stdoutput = self.__format_str(stdoutput)
        erroutput = self.__format_str(erroutput)
        if stdoutput:
            print(">> stdout: %s" % stdoutput)
        if erroutput:
            print(">> stderr: %s" % erroutput)
        return stdoutput, erroutput

    def __convert_to_regex(self, wildcard_paths):
        """
        通配符转换为正则表达式
        :param wildcard_paths:
        :return:
        """
        return [fnmatch.translate(pattern) for pattern in wildcard_paths]

    def __get_path_filters(self, task_params):
        """
        获取过滤路径（工具按需使用），支持用户配置通配符和正则表达式2种格式的过滤路径表达式，该方法会将通配符转换为正则表达式，合并使用
        :param task_params:
        :return: 合并后的正则表达式过滤路径格式
        """
        # 用户输入的原始参数
        wildcard_include_paths = task_params["path_filters"].get("inclusion", [])
        wildcard_exclude_paths = task_params["path_filters"].get("exclusion", [])
        regex_include_paths = task_params["path_filters"].get("re_inclusion", [])
        regex_exlucde_paths = task_params["path_filters"].get("re_exclusion", [])

        print(">> 过滤路径原始配置：")
        print(">> 说明：")
        print(">> include - 只扫描指定文件, exclude - 过滤掉指定文件, 优先级: exclude > include (即：如果A文件同时匹配，会优先exclude，被过滤)")
        print("include（通配符格式）: %s" % wildcard_include_paths)
        print("exclude（通配符格式）: %s" % wildcard_exclude_paths)
        print("include（正则表达式格式）: %s" % regex_include_paths)
        print("exclude（正则表达式格式）: %s" % regex_exlucde_paths)

        # 通配符转换为正则表达式
        if wildcard_include_paths:
            converted_include_paths = self.__convert_to_regex(wildcard_include_paths)
            regex_include_paths.extend(converted_include_paths)
        if wildcard_exclude_paths:
            converted_exclude_paths = self.__convert_to_regex(wildcard_exclude_paths)
            regex_exlucde_paths.extend(converted_exclude_paths)

        print(">> 合并后过滤路径；")
        print("include（正则表达式格式）: %s" % regex_include_paths)
        print("exclude（正则表达式格式）: %s" % regex_exlucde_paths)
        return {"re_inclusion": regex_include_paths, "re_exclusion": regex_exlucde_paths}

    def __scan(self):
        """
        分析代码
        """
        # 代码目录直接从环境变量获取
        source_dir = os.environ.get("SOURCE_DIR", None)
        print("[debug] source_dir: %s" % source_dir)

        # 其他参数从task_request.json文件获取
        task_params = self.__get_task_params()

        # ------------------------------------------------------------------ #
        # 获取需要扫描的文件列表
        # 此处获取到的文件列表,已经根据项目配置的过滤路径过滤
        # 增量扫描时，从SCAN_FILES获取到的文件列表与从DIFF_FILES获取到的相同
        # ------------------------------------------------------------------ #
        scan_files_env = os.getenv("SCAN_FILES")
        if scan_files_env and os.path.exists(scan_files_env):
            with open(scan_files_env, "r") as rf:
                scan_files = json.load(rf)
                # print("[debug] files to scan: %s" % len(scan_files))
        
        scan_files = [path for path in scan_files if path.endswith(".sql")]

        issues = list()
        for path in scan_files:
            scan_cmds = ["sqlcheck", "-v", "-f", path]
            try:
                stdout, stderr = self.__run_cmd(scan_cmds)
            except Exception as err:
                print(f"scan {path} failed: %s" % str(err))
                continue
            
            if stderr:
                raise Exception(f"Tool exec error: {stderr}")

            issues.extend(self.handle_data(stdout, path))

        print("[debug] issues: %s" % issues)
        # 输出结果到指定的json文件
        with open("result.json", "w") as fp:
            json.dump(issues, fp, indent=2)
    
    def handle_data(self, stdout: str, path: str):
        issues = list()
        start = False
        msg = list()
        line_no = 0
        rule = None
        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith(f"[{path}]:"):
                rule = self.__convert(line.split(")")[-1].strip())
                start = True
                msg.append(line.split(":")[-1].strip())
            elif line.startswith("[Matching Expression:"):
                line_list = None
                if line.find("lines") != -1:
                    line_list = [int(line.split("lines")[-1].strip()[:-1])]
                else:
                    line_list = [int(num.strip()) for num in line.split("line")[-1].strip()[:-1].split(",")]
                for line_no in line_list:
                    issues.append({"path": path, "line": line_no, "column": 0, "msg": "\n".join(msg), "rule": rule})
                start = False
                msg = list()
                line_no = 0
                rule = None
            elif start:
                msg.append(line)
        return issues

    def __convert(self, one_string, space_character=" "):
        """
        one_string:输入的字符串
        space_character:字符串的间隔符，以其做为分隔标志
        """
        # 将字符串转化为list
        string_list = str(one_string).split(space_character)
        first = string_list[0].lower()
        others = string_list[1:]

        # str.capitalize():将字符串的首字母转化为大写
        others_capital = [word.capitalize() for word in others]
        others_capital[0:0] = [first]
        # 将list组合成为字符串，中间无连接符。
        hump_string = "".join(others_capital)

        return hump_string

    def __check_usable(self):
        """
        检查工具在当前机器环境下是否可用
        """
        # 这里只是一个demo，检查python3命令是否可用，请按需修改为实际检查逻辑
        check_cmd_args = ["sqlcheck", "--version"]
        try:
            stdout, stderr = self.__run_cmd(check_cmd_args)
        except Exception as err:
            print("tool is not usable: %s" % str(err))
            return False
        return True

    def run(self):
        self.init_env()
        args = self.__parse_args()
        if args.command == "check":
            print(">> check tool usable ...")
            is_usable = self.__check_usable()
            result_path = "check_result.json"
            if os.path.exists(result_path):
                os.remove(result_path)
            with open(result_path, "w") as fp:
                data = {"usable": is_usable}
                json.dump(data, fp)
        elif args.command == "scan":
            print(">> start to scan code ...")
            self.__scan()
        else:
            print("[Error] need command(check, scan) ...")


if __name__ == "__main__":
    SQLCheck().run()
