# Ont Axes

A dApp game runs on [Ontology](https://ont.io/) Blockchain. [ontaxes.github.io](https://ontaxes.github.io/ontaxes/)

# Introduction

Welcome to this funny game! In this dApp game our goal is to take these brilliant axes away by using a little ONG.

Each axe has it's own rounds, in each round you'll cope with other players who also like the same axe as you.

In each round, a axe is divided averagely into many parts, you'll deposit ONG to collect those parts. when all those parts are collected by players, the round goes into award process. Only one part could represent the axe and the owner of that part could take away the axe.

For example, the wooden axe is 10 ONG, in each round, it is divided into 50 average parts. Players deposit 0.2 ONG to get 1 part. For representing this ownership, every part is numbered, the number is taken from range [1, 50]. Players receipt part numbers to represent they are the owner of those associated parts.

For generating the lucky number, program treats the transaction time as a integer, and then accumulates all of the transactions time in the same round to produce a big number, this number could be overflow but it's doesn't matter. Then program use that big number divides 50 to get a remainder, uses this remainder plus 1 to produce the lucky number.

Eventually, the axe will be token away by the player who owns the part number which equals the lucky number. The bonus is from the ONG of axe minus game fee, the rate of game fee is 3%.
