<!--
biz-flow-recon 输出模板（粒度 C：单接口）。
本文件可被被分析项目里的 `biz-flow-recon/templates/endpoint.md` 覆盖。
仅当用户给了具体 URL 或类#方法名时使用。

要点：清晰优先——图、编号、labeled 短列表、几句话、一行话，按流程特点挑。
-->

# POST /api/transfer — 跨账户转账

已登录用户发起跨账户转账（com.acme.pay.TransferController#transfer，TransferController.java:58）。流程跨多服务，画图最清楚：

```mermaid
sequenceDiagram
    autonumber
    participant U as 已登录用户
    participant T as TransferController
    participant GW as GwController (pay-gw)
    participant L as ledger 库
    participant CH as channel.example.com

    U->>T: POST /api/transfer
    T->>T: HMAC-SHA256 签名报文
    T->>GW: POST /v2/transfer (X-Sign)
    GW->>L: INSERT trade / UPDATE balance
    GW->>CH: 转发支付报文
    CH-->>GW: 受理回执
    GW-->>T: 受理回执
    T-->>U: 200
    Note over T: 异步写 /var/log/acme/pay.log
```

关键事实补充：
- **第三方交互（内部网关）**：调 `http://internal-pay/v2/transfer`，POST `application/json`，Header `X-Sign: <hex>`，body 含金额、账户、订单号；客户端 OkHttp（PayClient.java:71）。对端实现 com.acme.pay.gw.GwController#transfer（services/pay-gw/.../GwController.java:39）
- **第三方交互（外部通道）**：网关把请求转发到 `https://channel.example.com`
- **加解密**：`HMAC-SHA256` 签名外呼报文——避免支付通道篡改
- **数据库**：网关用 MyBatis `mapper/TransferMapper.xml` 在 `ledger` 表里 INSERT trade / UPDATE balance
- **日志**：异步追加一行到 `/var/log/acme/pay.log`

代码位置：`src/main/java/com/acme/pay/`、`services/pay-gw/`。

## 未跟到的引用

仅当存在未在工作区找到的下钻目标时才写这一节；没有就**整节略掉**。
