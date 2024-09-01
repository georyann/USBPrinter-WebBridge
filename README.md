## USBPrinter WebBridge

USBPrinter WebBridge 是一个轻量级的web程序，旨在无缝地将您的USB打印机转换为网络打印机，允许任何连接到网络的设备进行远程打印。

本Web应用前端使用纯HTML，后端基于Python和Flask框架，使用CUPS进行打印机的管理。支持自动保存用户上传的文件并记录用户上传的文件名、ip地址及操作系统。

1. 允许的文件格式：允许的文件格式为 pdf, txt, doc, docx, jpg, jpeg, png。可通过修改后端php增加文件格式列表拓展。
2. 获取公网IP：使用第三方API ipify 来获取客户端的公网IP地址。
3. 记录日志：记录上传文件的文件名、上传时间、公网IP地址和客户端操作系统信息。



### 前提条件

- 一台拥有USB接口的Linux设备
- 将你的打印机通过USB线缆连接至Linux设备
- 保证Linux设备连接至网络

### 测试环境

**CentOS Stream 9**  *不建议使用MacOS等Unix系统，因为为MacOS开发的打印机驱动程序在CUPS上不可用*

**python 3.9**



---

### 快速配置

*此处以CentOS Stream 9 & HP LaserJet M1136 MFP打印机为例*

***不同Linux发行版本配置命令会稍有差别，请适当修改***



#### 首先，确保您的系统是最新的

```bash
sudo yum update
```

#### 安装CUPS

1. 安装CUPS：

   ```bash
   sudo yum install cups
   ```

2. 启动CUPS服务并设置为开机启动：

   ```bash
   sudo systemctl start cups
   sudo systemctl enable cups
   ```

3. 确认CUPS服务是否正在运行：

   ```bash
   sudo systemctl status cups
   ```

#### *安装HPLIP

*根据你的打印机型号选择对应的驱动，**此处以为HP打印机为例**。*

1. 安装EPEL存储库

   HPLIP依赖于一些EPEL（Extra Packages for Enterprise Linux）存储库中的软件包，因此需要先安装EPEL存储库：

```bash
sudo yum install epel-release
```

2. 安装HPLIP

```bash
sudo yum install hplip
```

#### 配置和使用CUPS

1. 启动并启用CUPS服务

   ```bash
   sudo systemctl start cups
   sudo systemctl enable cups
   ```

2. 安装完毕后，可以通过浏览器访问CUPS的Web界面进行配置。打开浏览器并访问：

   ```
    http://<服务器IP地址>:631
   ```

   如果无法访问，请继续以下步骤。

   1. **打开防火墙端口**

      ```bash
      sudo firewall-cmd --permanent --add-port=631/tcp
      sudo firewall-cmd --reload
      ```

   2. **验证端口是否开放**
      使用`nmap`或`telnet`来检查631端口是否对外开放：

      ```bash
      nmap -p 631 <服务器IP地址>
      ```

      或者

      ```bash
      telnet <服务器IP地址> 631
      ```

3. 在Web界面中，添加打印机并共享添加的打印机。

   <img src="https://pico-1253511019.cos.ap-nanjing.myqcloud.com/202409011950292.png" alt="image-20240901144921828" style="zoom: 25%;" />

   

   有多个打印机选项时请选择带有USB字样的打印机

   <img src="https://pico-1253511019.cos.ap-nanjing.myqcloud.com/202409011950742.png" alt="image-20240901145047089" style="zoom:33%;" />

   勾选共享打印机

   <img src="https://pico-1253511019.cos.ap-nanjing.myqcloud.com/202409011950300.png" alt="image-20240901145225053" style="zoom:25%;" />

   选择与打印机型号匹配的驱动程序

   <img src="https://pico-1253511019.cos.ap-nanjing.myqcloud.com/202409011950383.png" alt="image-20240901145526259" style="zoom:33%;" />

   打印测试页面以测试打印机是否正常工作

#### 安装Python和Flask

如果尚未安装Python和pip，请先安装：

```bash
sudo yum install python3
sudo yum install python3-pip
```

然后使用pip安装Flask与 `pycups` 库以便与CUPS进行交互：

```bash
sudo pip3 install flask
sudo pip3 install flask pycups
```

#### 克隆仓库里的Flask应用并运行

1. 克隆GitHub仓库

```bash
git clone https://github.com/georyann/USBPrinter-WebBridge.git
```

2. 运行Flask应用

   1. 赋予 `start.sh` 脚本执行权限：

      ```bash
      chmod +x start.sh
      ```

   2. 运行脚本：

      ```bash
      ./start.sh
      ```

您应该会看到类似以下的输出：

```plaintext
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

#### 访问Web应用

打开浏览器，并访问：

```plaintext
http://<服务器IP地址>:5000
```

#### *开放防火墙端口（如果需要）

如果您的CentOS服务器启用了防火墙，并且您需要从外部访问Web应用，您可能需要开放5000端口：

```bash
sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```



**🎉恭喜你，现在已经可以通过局域网访问`http://<服务器IP地址>:5000`实现局域网内web页面打印了！**

**Tips：对于服务器，可设置start.sh脚本开机自动启动**



---

### 通过免费的内网穿透服务实现外网访问

*此处以cloudflare tunnels为例*

#### 前提条件

* 一个 Cloudflare 账号

- 一个已添加到 Cloudflare 的域名。

- 本地服务器的访问权限（如终端或SSH）

#### 步骤

1. 登陆至 cloudflare操作面板/仪表盘
2. 左侧Zero Trust➡️Networks➡️Tunnels
3. 根据提示选择你的操作系统，安装`cloudflared`，使用对应的**启动命令**即可实现内网穿透 

**Tips：可将获取到的启动命令添加至`start.sh`脚本末尾以实现一键启动cloudflare tunnels**

#### 参考文档

- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Cloudflared GitHub 仓库](https://github.com/cloudflare/cloudflared)



---

### 实验性

对于cloudflare tunnels在中国大陆地区访问不畅，我曾酌情选择cpolar实现内网穿透。由于免费版cpolar提供的三级域名会不定期更新，为了固定访问域名，可使用[dynu](https://www.dynu.com)提供的免费301web转发服务间接实现。

一键启动cpolar并通过正则表达式获取三级域名请参阅脚本`./Projects/get_cpolar_address.py`。

#### 参考文档

[Dynu API Resources](https://www.dynu.com/en-US/Resources/API)
