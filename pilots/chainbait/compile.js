const solc = require(process.argv[2] + '/node_modules/solc');
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/Bait.sol', 'utf8');
const out = JSON.parse(solc.compile(JSON.stringify({language: 'Solidity', sources: {'Bait.sol': {content: src}},
  settings: {outputSelection: {'*': {'*': ['abi', 'evm.bytecode.object']}}}})));
if (out.errors) out.errors.forEach(e => console.error(e.formattedMessage));
const c = {};
for (const [n, v] of Object.entries(out.contracts['Bait.sol'])) c[n] = {abi: v.abi, bin: v.evm.bytecode.object};
fs.writeFileSync(__dirname + '/build.json', JSON.stringify(c));
console.log('compiled', Object.keys(c));
