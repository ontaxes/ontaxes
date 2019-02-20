<template>
  <div>
    <carousel-3d
      class="axe"
      :width="400"
      :height="400"
      @after-slide-change="onAfterSlideChange"
      @before-slide-change="onBeforeSlideChange"
    >
      <slide v-for="(axe, i) in axes" :key="i" :index="i">
        <i :class="axe.key" @click="chooseBidPlan"></i>
        <div
          :class="{status: true, 'shake': shakingInfo && shakingInfoKey == axe.key, 'shake-constant': shakingInfo, 'shake-constant--hover': true}"
          @click="showInfo"
        >
          <div class="row">{{ axe.key | capitalize }} = {{ axe.price | ong }} ONG</div>
          <div class="row">{{ axe.cur_cnt }} / {{ axe.part_count }}</div>
        </div>
      </slide>
    </carousel-3d>

    <modal
      name="choose-bid-plan"
      :classes="['choose-bid-plan']"
      :width="330"
      :height="'auto'"
      transition="nice-modal-fade"
    >
      <h3>Wow such a brilliant {{ curAxe.key }} axe I can't wait to take it!</h3>
      <div class="bid-method">
        <div
          class="method"
          :class="{disabled: isBidMethodDisabled('cyano')}"
          @click="showDisabledReason('cyano')"
        >
          <input
            :disabled="isBidMethodDisabled('cyano')"
            type="radio"
            name="bid-method"
            id="bid-method-cyano"
            value="cyano"
            v-model="bidMethod"
          >
          <label for="bid-method-cyano">Cyano Wallet</label>
        </div>
        <i></i>
        <div
          class="method"
          :class="{disabled: isBidMethodDisabled('onto')}"
          @click="showDisabledReason('onto')"
        >
          <input
            type="radio"
            :disabled="isBidMethodDisabled('onto')"
            name="bid-method"
            id="bid-method-onto"
            value="onto"
            v-model="bidMethod"
          >
          <label for="bid-method-onto">ONTO Wallet</label>
        </div>
      </div>
      <div class="items">
        <div class="item" v-for="(plan, i) in bidPlans" :key="i" @click="buyAxe(plan)">
          <div :class="['coin', plan.name]"></div>
          <div class="count">{{ plan.value }} ONG</div>
        </div>
      </div>
    </modal>

    <modal
      name="bid-qrcode"
      :classes="['bid-qrcode']"
      :width="270"
      :height="'auto'"
      transition="nice-modal-fade"
    >
      <qrcode :value="bidQRCode" :options="{ width: 200, color: { dark: '#157FFB' }, margin: 2 }"></qrcode>
      <div class="tips">Open ONTO then scan above QRCode</div>
    </modal>

    <modal
      name="axe-info"
      :classes="['axe-info']"
      :height="'auto'"
      transition="nice-modal-fade"
      @opened="onAxeInfoOpened"
    >
      <tabs :options="{ useUrlFragment: false }">
        <tab name="Current">
          <div class="tab-content">
            <h3>{{ curAxe.key | capitalize }} axe #{{ curAxe.sn }}</h3>
            <table class="fixed_headers records">
              <thead>
                <tr>
                  <td>Address</td>
                  <td>ONG</td>
                  <td>Tickets</td>
                  <td>Time</td>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(record, i) in currentRecords" :key="i">
                  <td>
                    <a :href="record.addrLink" target="_blank">{{ record.addr }}</a>
                  </td>
                  <td>{{ record.bid | ong }}</td>
                  <td>
                    <div class="tickets" :title="record.tickets">{{ record.tickets }}</div>
                  </td>
                  <td>{{ record.time }}</td>
                </tr>
              </tbody>
            </table>
            <div class="no-records" v-show="currentRecords.length == 0">no record</div>
          </div>
        </tab>
        <tab name="Past">
          <div class="tab-content">
            <h3>
              {{ curAxe.key | capitalize }} axe #
              <input
                min="1"
                type="number"
                placeholder="serial number"
                v-model="pastSnInput"
                v-on:keyup.enter="enterPastSn($event)"
              > or from
              <select v-model="pastSnSelectEl">
                <option value>I'd played</option>
                <option v-for="(item, i) in boughtList" :value="item" :key="i">{{ item }}</option>
              </select>
            </h3>
            <h4 v-show="pastResult">#{{ pastSn }}</h4>
            <table v-show="pastResult" class="past-result">
              <tr>
                <td>Lucky address:</td>
                <td>
                  <a target="_blank" :href="pastResult.addrLink">{{ pastResult.luckyAddr }}</a>
                </td>
              </tr>
              <tr>
                <td>Bonus:</td>
                <td>{{ pastResult.bonus | ong }} ONG</td>
              </tr>
              <tr>
                <td>Lucky number:</td>
                <td>{{ pastResult.luckyNumber }}</td>
              </tr>
            </table>
            <div class="more-records" v-show="pastResult && pastRecords.length == 0">
              <a href="#" v-on:click.prevent="loadPastRecords">show records</a>
            </div>
            <table class="fixed_headers records" v-show="pastResult && pastRecords.length">
              <thead>
                <tr>
                  <td>Address</td>
                  <td>ONG</td>
                  <td>Tickets</td>
                  <td>Time</td>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(record, i) in pastRecords" :key="i">
                  <td>
                    <a href="record.addrLink" target="_blank">{{ record.addr }}</a>
                  </td>
                  <td>{{ record.bid | ong }}</td>
                  <td>
                    <div class="tickets" :title="record.tickets">{{ record.tickets }}</div>
                  </td>
                  <td>{{ record.time }}</td>
                </tr>
              </tbody>
            </table>
            <div class="no-records" v-show="!pastResult">no record</div>
          </div>
        </tab>
      </tabs>
    </modal>

    <a href="#" class="help" v-on:click.prevent="showHelp">Help?</a>
    <modal
      name="help"
      :classes="['help-dialog']"
      :width="500"
      :height="'auto'"
      transition="nice-modal-fade"
    >
      <div class="content">
        <div class="lang">
          <a href="#" :class="{active: helpLang == 'en'}" @click.prevent="helpLang = 'en'">EN</a>
          |
          <a
            href="#"
            :class="{active: helpLang == 'cn'}"
            @click.prevent="helpLang = 'cn'"
          >CN</a>
        </div>
        <div class="en" v-show="helpLang == 'en'">
          <p>Welcome to this funny game! In this dApp game our goal is to take these brilliant axes away by using a little ONG.</p>
          <p>
            Every axe has it's own rounds, in each round you'll cope with other players who also like the same axe as
            you.
          </p>
          <p>
            In each round, a axe is divided averagely into many parts, you'll deposit ONG to collect those parts. when all those
            parts are collected by players, the round goes into award process. Only one part could represent the axe
            and the owner of that part could take away the axe.
          </p>
          <p>
            For example, the wooden axe is 10 ONG, in each round, it is divided into 50 average parts. Players deposit 0.2 ONG to get
            1 part. For representing this ownership, every part is numbered, the number is taken from range [1, 50]. Players receipt
            part numbers to represent they are the owner of those associated parts.
          </p>
          <p>
            For generating the lucky number, program treats the transaction time as a integer, and then accumulates all of
            the transactions time in the same round to produce a big number, this number could be overflow but it's doesn't
            matter. Then program use that big number divides 50 to get a remainder, uses this remainder plus 1 to produce the
            lucky number.
          </p>
          <p>
            Eventually, the axe will be token away by the player who owns the part number which equals the lucky number. The bonus is
            from the ONG of axe minus game fee, the rate of game fee is 3%.
          </p>
        </div>
        <div class="cn" v-show="helpLang == 'cn'">
          <p>欢迎来到这个买斧头的小游戏。如你所见，在这个 dApp 游戏中有几把炫彩夺目的斧头，我们的目标就是使用一点点 ONG 来带走它们。</p>
          <p>每个斧头都有属于自己的轮次，在每一轮中你需要和那些与你看中同一个斧头的玩家们进行竞争。</p>
          <p>
            在每一轮中，一个斧头被平均分成若干份，你需要使用 ONG 来收集这些部件。当所有部件都被玩家们收集后，轮次进入奖励阶段。只有一个部件可以代表斧头，
            获得那个部件的玩家可以拿走斧头。
          </p>
          <p>
            比如，木质斧头是 10 ONG，在每一轮中，它被等分为 50 份。玩家使用 0.2 ONG 可以收集 1 份。为了表示这个所有关系，每个部件都已被编号，号码来自区间 [1, 50]。
            玩家会收到其所收集的部件号，以此表示他们是那些部件的拥有者。
          </p>
          <p>
            为了生成幸运号码，程序将交易时间当做整数，并将一个轮次中的所有交易时间进行累加，等到一个大的整数。这个整数有可能会溢出，不过不碍事。然后程序使用这个大的整数除以 50 得到
            一个余数，使用该余数加上 1 得到幸运号码。
          </p>
          <p>最后，斧头会被拥有和幸运号码相同的部件号的玩家带走。奖励就是斧头的 ONG 减去游戏费用。游戏费用的费率为 3%。</p>
        </div>
        <a class="bug" href="https://github.com/ontaxes/ontaxes/issues" target="_blank">report bug</a>
      </div>
    </modal>

    <modal
      name="disabled-reason-cyano"
      :classes="['disabled-reason', 'cyano']"
      :width="500"
      :height="'auto'"
      transition="nice-modal-fade"
    >
      <div>cyano</div>
    </modal>

    <modal
      name="disabled-reason-onto"
      :classes="['disabled-reason','onto']"
      :width="500"
      :height="'auto'"
      transition="nice-modal-fade"
    >
      <div>
        <h3>This method is not currently supported</h3>
        <p>
          Deposit via
          <a target="_blank" href="https://onto.app/">ONTO</a> QRCode sanning is not currently supported, but will be avaiable ASAP after the ONTO's official
          upgrades, stay tuned.
        </p>
      </div>
    </modal>
  </div>
</template>
<script>
import { Api, WsClient } from "../lib";
import { Crypto, utils } from "ontology-ts-sdk";
import moment from "moment";

const defaultPastResult = {
  bonus: 0,
  luckyAddr: "",
  luckyNumber: "",
  addrLink: ""
};

const hex2str = stuff => utils.hexstr2str(stuff);
const hex2addr = stuff => {
  const addr = new Crypto.Address(stuff);
  return addr.toBase58();
};
const addrLink = addr => "https://explorer.ont.io/address/" + addr;
const map2obj = m => {
  if (!m.forEach) return m;

  const obj = {};
  m.forEach((v, k) => (obj[k] = v));
  return obj;
};

export default {
  name: "axes",
  data() {
    return {
      axes: [
        { key: "wooden", part_count: 0, part_price: 0, sn: 1, cur_cnt: 0 },
        { key: "stone", part_count: 0, part_price: 0, sn: 1, cur_cnt: 0 },
        { key: "iron", part_count: 0, part_price: 0, sn: 1, cur_cnt: 0 },
        { key: "gold", part_count: 0, part_price: 0, sn: 1, cur_cnt: 0 },
        { key: "diamond", part_count: 0, part_price: 0, sn: 1, cur_cnt: 0 }
      ],
      curAxe: {},
      bidPlans: [
        { name: "cooper", value: 0 },
        { name: "silver", value: 0 },
        { name: "gold", value: 0 }
      ],
      isSliding: false,
      isCyanoWalletEnable: false,
      bidMethod: "onto",
      ws: null,
      currentRecords: [],
      pastSn: "",
      pastResult: Object.assign({}, defaultPastResult),
      pastRecords: [],
      boughtList: [],
      pastSnSelectEl: "",
      pastSnInput: "",
      shakingInfo: false,
      shakingInfoKey: "",
      helpLang: "en",
      bidQRCode: "",
      disabledReason: {
        cyano: "disabled-reason-cyano",
        onto: "disabled-reason-onto"
      }
    };
  },
  filters: {
    capitalize(text) {
      if (!text) return;
      return text[0].toUpperCase() + text.slice(1);
    },
    ong(text) {
      if (!text) return;
      return (parseFloat(text) / 1e9).toFixed(1);
    }
  },
  created() {
    this.init();
  },
  watch: {
    curAxe() {
      this.updatePlans();
    },
    pastSnSelectEl: function(val) {
      const sn = parseInt(val);
      if (!sn) return;
      this.pastSnInput = "";
      this.loadPastResult(sn);
    }
  },
  methods: {
    async init() {
      const loader = this.$loading.show({
        color: "#167FFB",
        container: document.body,
        canCancel: false
      });

      this.isCyanoWalletEnable = await Api.isCyanoWalletEnable();
      if (!this.isCyanoWalletEnable) {
        loader.hide();
        this.$toasted.error(
          "<a href='https://chrome.google.com/webstore/detail/cyano-wallet/dkdedlpgdmmkkfjabffeganieamfklkm' target='_blank'>" +
            "Cyano Wallet</a>&nbsp;is required to play this game.",
          {
            position: "top-center"
          }
        );
        return;
      }

      this.bidMethod = "cyano";
      await Api.initContractIfNeeded();
      await this.loadeAxes();
      await this.setupWs();

      loader.hide();
    },
    updateLocalAxe(axe) {
      axe = map2obj(axe);
      axe.key = hex2str(axe.key);
      axe.cur_cnt = axe.cur_amount / axe.part_price;
      const local = this.getLocalAxe(axe.key);
      Object.assign(local, axe);
    },
    async loadeAxes() {
      const axes = await Api.queryAxes();
      axes.forEach(axe => this.updateLocalAxe(axe));
      this.curAxe = this.axes[0];
    },
    async setupWs() {
      this.ws = new WsClient();
      await this.ws.connect();
      this.ws.onNotify = async (action, data) => {
        if (["buy_axe", "award"].indexOf(action) !== -1) {
          const axeKey = hex2str(data[0]);
          await this.refreshAxe(axeKey);
        }
      };
    },
    getLocalAxe(key) {
      for (let i = 0, len = this.axes.length; i < len; i++) {
        const axe = this.axes[i];
        if (axe.key === key) return axe;
      }
      return null;
    },
    chooseBidPlan() {
      if (this.isSliding) return;
      this.$modal.show("choose-bid-plan");
    },
    onBeforeSlideChange() {
      this.isSliding = true;
      this.$modal.hide("choose-bid-plan");
      this.$modal.hide("axe-info");
      this.pastResult = Object.assign({}, defaultPastResult);
      this.pastRecords = [];
      this.pastSn = "";
      this.pastSnSelectEl = "";
    },
    onAfterSlideChange(idx) {
      this.isSliding = false;
      this.curAxe = this.axes[idx];
    },
    updatePlans() {
      const factors = [1, 3, 5];
      this.bidPlans.forEach((plan, i) => {
        plan.value = ((this.curAxe.part_price / 1e9) * factors[i]).toFixed(1);
      });
    },
    showQRCode() {
      this.$modal.show("bid-qrcode");
    },
    async buyAxe(plan) {
      if (this.bidMethod === "onto") {
        this.buyAxeOnto(plan);
      } else {
        await this.buyAxeCyano(plan);
      }
    },
    buyAxeOnto(plan) {
      const qrcodeUrl =
        "https://ontaxes.github.io/bid-qrcode/" +
        [this.curAxe.key, plan.value].join("/");

      const payload = {
        action: "invoke",
        version: "v1.0.0",
        params: {
          login: true,
          qrcodeUrl
        }
      };

      this.bidQRCode = JSON.stringify(payload);
      this.showQRCode();
    },
    async buyAxeCyano(plan) {
      try {
        await Api.buyAxe(this.curAxe.key, plan.value);
        this.$toasted.success("Deposit succeed", {
          position: "top-center",
          duration: 2000
        });
        this.$modal.hide("choose-bid-plan");
      } catch (e) {
        if (e === "CANCELED") {
          this.$toasted.info("Transaction canceled", {
            position: "top-right",
            duration: 2000
          });
          return;
        }

        if (typeof e === "string" && e.indexOf("no balance enough") !== -1) {
          this.$toasted.error("Transaction failed: no balance enough", {
            position: "top-right",
            duration: 3000
          });
        }
      }
    },
    async refreshAxe(key) {
      const axe = await Api.queryAxe(key);
      this.updateLocalAxe(axe);
      this.shakingInfo = true;
      this.shakingInfoKey = key;
      setTimeout(() => {
        this.shakingInfo = false;
        this.shakingInfoKey = "";
      }, 1000);
    },
    showInfo() {
      this.$modal.show("axe-info");
    },
    onAxeInfoOpened() {
      this.loadCurrentRecords();
      this.loadBoughtList();
    },
    async loadBoughtList() {
      const res = await Api.queryBuyerBought();
      const axe = this.curAxe;
      const list = res
        .map(item => map2obj(item))
        .filter(item => hex2str(item.key) === axe.key)
        .map(item => item.sn);
      this.boughtList = list;
    },
    async loadCurrentRecords() {
      const loader = this.$loading.show({
        color: "#167FFB",
        container: document.querySelector("#current"),
        canCancel: false
      });
      const axe = this.curAxe;
      const result = await Api.queryRoundRecords(axe.key, axe.sn);
      this.currentRecords = result
        .map(r => map2obj(r))
        .sort((a, b) => b.time - a.time)
        .map(r => ({
          addr: hex2str(r.buyer),
          bid: r.bid,
          time: moment(r.time * 1000).format("YYYY-MM-DD HH:mm:ss"),
          addrLink: addrLink(hex2str(r.buyer)),
          tickets: r.tickets.join(", ")
        }));
      loader.hide();
    },
    enterPastSn(evt) {
      const sn = parseInt(evt.target.value);
      if (!sn) return;
      this.pastSnSelectEl = "";
      this.loadPastResult(sn);
    },
    async loadPastResult(sn) {
      const loader = this.$loading.show({
        color: "#167FFB",
        container: document.querySelector("#current"),
        canCancel: false
      });

      try {
        this.pastSn = sn;
        const result = await Api.queryRoundResult(this.curAxe.key, sn);
        const addr = hex2addr(result.get("to_acc"));
        this.pastResult = {
          bonus: result.get("bonus"),
          luckyNumber: result.get("lucky"),
          luckyAddr: addr,
          addrLink: addrLink(addr)
        };
        this.pastRecords = [];
      } catch (e) {
        this.pastResult = false;
      }
      loader.hide();
    },
    async loadPastRecords() {
      const loader = this.$loading.show({
        color: "#167FFB",
        container: document.querySelector("#current"),
        canCancel: false
      });

      try {
        const result = await Api.queryRoundRecords(
          this.curAxe.key,
          this.pastSn
        );
        this.pastRecords = result
          .map(r => map2obj(r))
          .sort((a, b) => b.time - a.time)
          .map(r => ({
            addr: hex2str(r.buyer),
            bid: r.bid,
            time: moment(r.time * 1000).format("YYYY-MM-DD HH:mm:ss"),
            addrLink: addrLink(hex2str(r.buyer)),
            tickets: r.tickets.join(", ")
          }));
      } catch (e) {
        this.pastResult = false;
        this.pastRecords = [];
      }
      loader.hide();
    },
    showHelp() {
      this.$modal.show("help");
    },
    isBidMethodDisabled(method) {
      if (method === "cyano") {
        return !this.isCyanoWalletEnable;
      }
      if (method === "onto") {
        return true;
      }
    },
    showDisabledReason(method) {
      if (this.isBidMethodDisabled(method)) {
        this.$modal.show(this.disabledReason[method]);
      }
    }
  }
};
</script>
<style>
.carousel-3d-slide {
  text-align: center !important;
  background-color: #7cc1ff !important;
  border-radius: 5px !important;
  border-color: cornflowerblue !important;
  color: #fff;
  cursor: pointer;
}

.carousel-3d-slide i {
  display: inline-block;
  width: 300px;
  height: 300px;
  margin-top: 20px;
}

.carousel-3d-slide i.wooden {
  background: url("../assets/images/axe_wooden.png") no-repeat center;
  background-size: contain;
}

.carousel-3d-slide i.stone {
  background: url("../assets/images/axe_stone.png") no-repeat center;
  background-size: contain;
}

.carousel-3d-slide i.iron {
  background: url("../assets/images/axe_iron.png") no-repeat center;
  background-size: contain;
}

.carousel-3d-slide i.gold {
  background: url("../assets/images/axe_gold.png") no-repeat center;
  background-size: contain;
}

.carousel-3d-slide i.diamond {
  background: url("../assets/images/axe_diamond.png") no-repeat center;
  background-size: contain;
}

.carousel-3d-slide .status {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  margin: 0 auto;
}

.carousel-3d-slide .status .row {
  padding: 3px 0;
}

.carousel-3d-container.axe {
  position: absolute !important;
  top: 50%;
  left: 0;
  right: 0;
  margin: 0 auto;
  transform: translate(0, -50%);
}

.carousel-3d-slide.current i:hover {
  animation-name: spaceboots;
  animation-duration: 1s;
  transform-origin: 50% 50%;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}

@keyframes spaceboots {
  0% {
    transform: translate(2px, 1px) rotate(0deg);
  }
  10% {
    transform: translate(-1px, -2px) rotate(-1deg);
  }
  20% {
    transform: translate(-3px, 0px) rotate(1deg);
  }
  30% {
    transform: translate(0px, 2px) rotate(0deg);
  }
  40% {
    transform: translate(1px, -1px) rotate(1deg);
  }
  50% {
    transform: translate(-1px, 2px) rotate(-1deg);
  }
  60% {
    transform: translate(-3px, 1px) rotate(0deg);
  }
  70% {
    transform: translate(2px, 1px) rotate(-1deg);
  }
  80% {
    transform: translate(-1px, -1px) rotate(1deg);
  }
  90% {
    transform: translate(2px, 2px) rotate(0deg);
  }
  100% {
    transform: translate(1px, -2px) rotate(-1deg);
  }
}

.status {
  margin-top: 5px;
  font-size: 16px;
}

.choose-bid-plan {
  border-radius: 5px;
  background: #f7f7f7;
  box-shadow: 5px 5px 30px 0px rgba(46, 61, 73, 0.6);
}

.choose-bid-plan .items {
  display: flex;
  list-style: none;
  justify-content: space-around;
  padding: 0 0 20px 0;
}

.choose-bid-plan .items .item {
  text-align: center;
  cursor: pointer;
  width: 60px;
}

.choose-bid-plan .items .item .coin {
  display: inline-block;
  width: 32px;
  height: 32px;
  position: relative;
  transition: all 0.2s ease-in-out 0s;
  top: 0;
}

.choose-bid-plan .items .item:hover .coin {
  top: -5px;
}

.choose-bid-plan .items .item .coin.cooper {
  background: url("../assets/images/coin_single_cooper.png") no-repeat center;
  background-size: contain;
}

.choose-bid-plan .items .item .coin.silver {
  background: url("../assets/images/coin_single_silver.png") no-repeat center;
  background-size: contain;
}

.choose-bid-plan .items .item .coin.gold {
  background: url("../assets/images/coin_single_gold.png") no-repeat center;
  background-size: contain;
}

.choose-bid-plan .items .item .count {
  padding-top: 5px;
}

.choose-bid-plan h3 {
  text-align: center;
  font-size: 12px;
  font-weight: normal;
  margin-top: 20px;
}

.choose-bid-plan .via {
  text-align: center;
  margin: 10px 0;
}

.choose-bid-plan .bid-method {
  text-align: center;
  padding: 10px 0 15px 0;
}

.choose-bid-plan .bid-method .method {
  display: inline-block;
}

.choose-bid-plan .bid-method i {
  display: inline-block;
  width: 20px;
}

.choose-bid-plan .bid-method label {
  cursor: pointer;
  padding-left: 3px;
}

.choose-bid-plan .bid-method .method.disabled > * {
  color: #666;
  cursor: help;
}

.bid-qrcode {
  background: #fff;
  border-radius: 3px;
  text-align: center;
  padding-top: 10px;
}

.bid-qrcode .tips {
  padding: 0 0 15px 0;
}

.vld-overlay {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  align-items: center;
  display: none;
  justify-content: center;
  overflow: hidden;
  z-index: 1;
  cursor: wait;
}

.vld-overlay.is-active {
  display: flex;
}

.vld-overlay.is-full-page {
  z-index: 999;
  position: fixed;
}

.vld-overlay .vld-background {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  background: #fff;
  opacity: 0.5;
}

.vld-overlay .vld-icon {
  position: relative;
}

.vld-parent {
  position: relative;
}

.toasted-container.top-right {
  top: 10px !important;
  right: 20px !important;
}

.tabs-component {
  margin: 4em 0;
}

.tabs-component-tabs {
  border: solid 1px #ddd;
  border-radius: 6px;
  margin-bottom: 5px;
  padding-left: 20px;
}

@media (min-width: 700px) {
  .tabs-component-tabs {
    border: 0;
    align-items: stretch;
    display: flex;
    justify-content: flex-start;
    margin-bottom: -1px;
  }
}

.tabs-component-tab {
  color: #999;
  font-size: 14px;
  font-weight: 600;
  margin-right: 0;
  list-style: none;
}

.tabs-component-tab:not(:last-child) {
  border-bottom: dotted 1px #ddd;
}

.tabs-component-tab:hover {
  color: #666;
}

.tabs-component-tab.is-active {
  color: #000;
}

.tabs-component-tab.is-disabled * {
  color: #cdcdcd;
  cursor: not-allowed !important;
}

@media (min-width: 700px) {
  .tabs-component-tab {
    background-color: #fff;
    border: solid 1px #ddd;
    border-radius: 3px 3px 0 0;
    margin-right: 0.5em;
    transform: translateY(2px);
    transition: transform 0.3s ease;
  }

  .tabs-component-tab.is-active {
    border-bottom: solid 1px #fff;
    z-index: 2;
    transform: translateY(0);
  }
}

.tabs-component-tab-a {
  align-items: center;
  color: inherit;
  display: flex;
  padding: 0.75em 1em;
  text-decoration: none;
}

.tabs-component-panels {
  position: relative;
}

@media (min-width: 700px) {
  .tabs-component-panels {
    background-color: #fff;
    border: solid 1px #ddd;
    border-radius: 3px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  }
}

.tab-content {
  min-height: 150px;
}

.tab-content .records {
  max-height: 200px;
  overflow: auto;
}

.tab-content h3 {
  text-align: center;
  font-size: 12px;
  margin: 10px 0;
  font-weight: normal;
}

.tab-content table {
  width: 100%;
  font-size: 12px;
  border-collapse: collapse;
}

.fixed_headers thead tr {
  display: block;
  position: relative;
}

.tab-content table td {
  padding: 10px 8px;
}

.tab-content table thead td {
  border-bottom: 1px solid #e8e8e8;
}

a {
  color: #1890ff;
}

.tab-content tbody tr {
  transition: all 0.3s, border 0s;
  background-color: #fff;
}

.tab-content tbody tr:hover {
  background-color: #e6f7ff;
}

.tab-content tbody td {
  border-bottom: 1px solid #e8e8e8;
}

.fixed_headers {
  width: 750px;
  table-layout: fixed;
  border-collapse: collapse;
}

.fixed_headers th {
  text-decoration: underline;
}

.fixed_headers th,
.fixed_headers td {
  padding: 5px;
  text-align: left;
}

.fixed_headers td:nth-child(1),
.fixed_headers th:nth-child(1) {
  min-width: 200px;
}

.fixed_headers td:nth-child(2),
.fixed_headers th:nth-child(2) {
  min-width: 200px;
}

.fixed_headers thead {
  background-color: #fafafa;
  color: rgba(0, 0, 0, 0.85);
}

.fixed_headers thead tr {
  display: block;
  position: relative;
}

.fixed_headers tbody {
  display: block;
  overflow: auto;
  width: 100%;
  max-height: 300px;
}

.fixed_headers.records td:nth-child(1),
.fixed_headers.records th:nth-child(1) {
  min-width: 260px;
}

.fixed_headers.records td:nth-child(2),
.fixed_headers.records th:nth-child(2) {
  min-width: 50px;
  padding-left: 10px;
}

.fixed_headers.records td:nth-child(3),
.fixed_headers.records th:nth-child(3) {
  width: 100px;
}

.fixed_headers.records thead td:nth-child(3) {
  width: 108px;
}

.fixed_headers.records .tickets {
  width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fixed_headers.records td:nth-child(4),
.fixed_headers.records th:nth-child(4) {
  width: 200px;
  white-space: nowrap;
}

.vld-overlay {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  align-items: center;
  display: none;
  justify-content: center;
  overflow: hidden;
  z-index: 1;
}

.vld-overlay.is-active {
  display: flex;
}

.vld-overlay.is-full-page {
  z-index: 999;
  position: fixed;
}

.vld-overlay .vld-background {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  background: #fff;
  opacity: 0.5;
}

.vld-overlay .vld-icon {
  position: relative;
}

.vld-parent {
  position: relative;
}

.no-records {
  text-align: center;
  padding-top: 30px;
  color: #434343;
  font-size: 14px;
}

.more-records {
  text-align: center;
  padding: 15px 0;
}

.more-records a {
  font-size: 12px;
}

.help {
  position: absolute;
  right: 20px;
  top: 10px;
  font-size: 14px;
}

.help-dialog .content {
  background-color: #fff;
  padding: 10px 20px;
  border-radius: 3px;
  font-size: 14px;
  position: relative;
}

.help-dialog .content a.bug {
  position: absolute;
  right: 15px;
  bottom: 10px;
  font-size: 12px;
}

.help-dialog .lang a.active {
  color: #999;
  text-decoration: none;
  cursor: default;
}

input {
  outline: none;
  margin-left: 3px;
}

h4 {
  margin: 0;
  padding-left: 10px;
  font-size: 14px;
  padding-bottom: 10px;
}

table.past-result td:first-child {
  width: 100px;
}

table.past-result td {
  border-bottom: 1px solid #d8d8d8;
}

.disabled-reason {
  background-color: #fff;
  border-radius: 3px;
  padding: 10px 20px;
}

.disabled-reason h3 {
  text-align: center;
  padding-bottom: 10px;
}

.toasted.toasted-primary.error a {
  color: #fff;
}
</style>
