华为云空间下载工具
==========================
# 介绍
该工具弥补华为官方的工具只能下载，无法跳过已经下载的文件的问题（他会重新创建一个新文件）。所以用起来非常的不方便，也不方便我们下载到电脑进行备份。

该工具的原理是模拟网页请求，拿到所有的文件的下载链接，然后生成cmdlist.sh，内含wget脚本类似：

```bash
wget -c -O IMG_20200729_145603.jpg "https://download-proxy-p01-drcn.platform.hicloud.com/filev2/1596006526/MDAwMTZBODp5_ZNMQ4gzYeqoxbSju81vUUyoPAS_g7JzWJ_K7vnSA../f3b36ef4707e15048773285137afe61a1ec32f/IMG_20200729_145603.jpg?key=AWqIQF8h9MAK6KCin_vpekFiChbtf-FvWPlqK8zUG5uVTKMaBQhyNg..&a=300086000123122433-a0433a4-92808-5840&nsp_ver=3.0"
wget -c -O IMG_20200729_145559_1.jpg "https://download-proxy-p01-drcn.platform.hicloud.com/filev2/1596006524/MDAwMTZBDj1IAkHNzKZb2CoDnDGPqF5G5seMAGAlJO5MP2qf-ABsQ../36f9e7f8fc4dc51ff85d73dd172f871e1f8979/IMG_20200729_145559_1.jpg?key=AWqIQF8h9MDDJlQsHI6DzGxXAa8pkBm0KcUzfwbe8PusVTIqpf7FKQ..&a=300086000123122433-a0433a4-92808-5840&nsp_ver=3.0"
wget -c -O IMG_20200729_145559.jpg "https://download-proxy-p01-drcn.platform.hicloud.com/filev2/1596007331/MDAwMTZBODkRKwPdWh6KQ2MwOSVcVFpB7EvDBYdt3ojHtysfVXg3A../651cd6c70b2345245d6192ca4d6366181d87ad/IMG_20200729_145559.jpg?key=AWqIQF8h9MDB4nslWmrNpYYR_IzYh_BrAV_Q4sTNV7Q_ZDNMt3XgMw..&a=300086000123122433-a0433a4-92808-5840&nsp_ver=3.0"
```

可以运行以下命令并发的下载。对于已经下载过的文件会自动跳过

```bash
parallen < cmdlist.sh
```

# 用法：
更新session.py中的cookie和header两项，可以再浏览器里面复制curl命令，然后放到 https://curl.trillworks.com/ 网站上生成cookie和header
