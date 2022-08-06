# tca_plugin_sqlcheck
A TCA plugin for [sqlcheck](https://github.com/jarulraj/sqlcheck).

## 依赖

sqlcheck 1.3

## 使用


## Q&A

### 执行异常
如遇到以下异常：
```log
$ ./sqlcheck -h
./sqlcheck: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by ./sqlcheck)
./sqlcheck: /lib64/libstdc++.so.6: version `CXXABI_1.3.8' not found (required by ./sqlcheck)
./sqlcheck: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by ./sqlcheck)
```
解决方案：
- 需要升级g++版本到4.9+

### 现有可执行文件不支持当前系统

解决方案：
- 可参考[sqlcheck readme](https://github.com/jarulraj/sqlcheck)文档，在当前系统中编译得到可执行文件后，拷贝到 [tools](tools/) 对应的目录下。

