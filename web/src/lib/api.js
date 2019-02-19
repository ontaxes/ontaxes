import { client } from "ontology-dapi";
import { utils, ScriptBuilder, WebsocketClient } from "ontology-ts-sdk";

const contractHash = "4f1e06b2d875520526eaddfb7142cba44f3c77f3";

client.registerClient({});

export const decode = stuff => {
  if (typeof stuff !== "string") return stuff;

  if (stuff === "00") return false;
  if (stuff === "01") return true;
  const sr = new utils.StringReader(stuff);
  return ScriptBuilder.deserializeItem(sr);
};

export class WsClient {
  constructor() {
    this.conn = null;
    this.heartBeatTimer = 0;
    this.onNotify = () => {};
  }

  async connect() {
    const node = await client.api.network.getNetwork();

    let url = "";
    if (node.type === "MAIN") {
      url = "wss://" + node.address + ":10335";
    } else {
      url = "ws://" + node.address + ":20335";
    }
    this.conn = new WebsocketClient(url, false, false);

    const param = {
      Action: "subscribe",
      Version: "1.0.0",
      ConstractsFilter: [contractHash],
      SubscribeEvent: true,
      SubscribeJsonBlock: true,
      SubscribeRawBlock: false,
      SubscribeBlockTxHashs: false
    };

    this.conn.addNotifyListener(async data => {
      if (!data || !data["Result"] || !data["Result"]["Notify"]) return;

      data = data["Result"]["Notify"];
      const rows = data.filter(d => d.ContractAddress === contractHash);
      if (rows.length === 0) return;

      const action = rows[0].States;
      const actionName = utils.hexstr2str(action[0]);

      if (this.onNotify) {
        action.shift();
        this.onNotify(actionName, action);
      }
    });
    await this.conn.send(param);

    if (this.heartBeatTimer) clearInterval(this.heartBeatTimer);
    this.heartBeatTimer = setInterval(() => this.conn.sendHeartBeat(), 1000);
  }
}

export class Api {
  static async isCyanoWalletEnable() {
    try {
      await client.api.provider.getProvider();
      return true;
    } catch (e) {
      return false;
    }
  }

  static async isInitialized() {
    return this.invokeRead("get_is_initialized", []);
  }

  static async initContractIfNeeded() {
    const isInitialized = await this.isInitialized();
    if (isInitialized) return;

    await this.init();
  }

  static async init() {
    return this.invoke("init", []);
  }

  static async queryAxes() {
    return this.invokeRead("query_axes");
  }

  static async upsertAxe(axe) {
    return this.invoke("upsert_axe", [
      { type: "String", value: axe.name },
      { type: "Integer", value: axe.partPrice },
      { type: "Integer", value: axe.partCount }
    ]);
  }

  static async buyAxe(key, bid) {
    bid = bid * 1e9;
    const buyer = await client.api.asset.getAccount();
    return this.invoke("buy_axe", [
      { type: "String", value: key },
      { type: "String", value: buyer },
      { type: "Integer", value: bid }
    ]);
  }

  static async queryRoundRecords(key, sn) {
    return this.invokeRead("query_round_records", [
      { type: "String", value: key },
      { type: "Integer", value: sn }
    ]);
  }

  static async queryAxe(key) {
    return this.invokeRead("query_axe", [{ type: "String", value: key }]);
  }

  static async queryRoundResult(key, sn) {
    return this.invokeRead("query_round_result", [
      { type: "String", value: key },
      { type: "Integer", value: sn }
    ]);
  }

  static async queryBuyerBought() {
    const buyer = await client.api.asset.getAccount();
    return this.invokeRead("query_buyer_bought", [
      { type: "String", value: buyer }
    ]);
  }

  static async invokeRead(method, params) {
    const res = await client.api.smartContract.invokeRead({
      scriptHash: contractHash,
      operation: method,
      args: params
    });
    return decode(res);
  }

  static async invoke(method, params) {
    const account = await client.api.asset.getAccount();
    const res = await client.api.smartContract.invoke({
      scriptHash: contractHash,
      operation: method,
      args: params,
      payer: account,
      gasLimit: 20600000,
      gasPrice: 500
    });
    return decode(res);
  }
}
