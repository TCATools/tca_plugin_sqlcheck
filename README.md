# tca_plugin_sqlcheck
A TCA plugin for [sqlcheck](https://github.com/jarulraj/sqlcheck).

## 依赖

sqlcheck 1.3

## 使用
- 部署好TCA
- 下载本插件
- 在TCA上加载本插件的[工具JSON](config/sqlcheck.json)
- 在TCA上的节点管理页面上，给节点添加本插件的工具进程
- 在待分析的TCA项目的分析方案中，添加本插件的规则，然后启动任务即可

## Q&A

### 执行异常
如遇到以下异常：
```log
$ ./sqlcheck -h
./sqlcheck: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by ./sqlcheck)
./sqlcheck: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.26' not found (required by ./sqlcheck)
./sqlcheck: /lib64/libstdc++.so.6: version `CXXABI_1.3.8' not found (required by ./sqlcheck)
./sqlcheck: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by ./sqlcheck)
```
解决方案：
方案一：
- 客户端执行机器需要升级g++版本到4.9+
- 设置LD_LIBRARY_PATH
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<gcc安装位置>/lib64
```
方案二：
- 使用TCA的[工具依赖功能](https://tencent.github.io/CodeAnalysis/zh/guide/%E5%B7%A5%E5%85%B7%E7%AE%A1%E7%90%86/%E8%87%AA%E5%AE%9A%E4%B9%89%E5%B7%A5%E5%85%B7.html#%E8%87%AA%E5%AE%9A%E4%B9%89%E5%B7%A5%E5%85%B7%E6%AD%A5%E9%AA%A4%E8%AF%B4%E6%98%8E)，添加gcc到TCA工具依赖中
- 将该插件安装到TCA上时候，设置上新增的gcc工具依赖即可

### 现有可执行文件不支持当前系统

解决方案：
- 可参考[sqlcheck readme](https://github.com/jarulraj/sqlcheck)文档，在当前系统中编译得到可执行文件后，拷贝到 [tools](tools/) 对应的目录下。

### 加载工具JSON时候提示语言不存在

解决方案：
- 在[工具JSON](config/sqlcheck.json)中，修改规则的languages字段对应值为`tsql`
