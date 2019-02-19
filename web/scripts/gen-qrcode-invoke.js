#!/usr/bin/env node

const axes = [
  { key: "wooden", part_price: 0.2 },
  { key: "stone", part_price: 0.5 },
  { key: "iron", part_price: 1 },
  { key: "gold", part_price: 1 },
  { key: "diamond", part_price: 2 }
];

const planFactors = [1, 3, 5];
const plans = [];

axes.forEach(axe => {
  planFactors.forEach(factor => {
    plans.push({ key: axe.key, value: axe.part_price * factor });
  });
});

plans.forEach(plan => {});
