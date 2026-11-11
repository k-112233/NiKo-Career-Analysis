// Smoke-test the actual shipped script and filtering without external JS packages.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:({team:'Falcons',game:'__all',start:'2015-01-01',end:'2026-11-10',metric:'kd',minimum:'10'})[id]??'',textContent:'',innerHTML:'',addEventListener(){},replaceChildren(...xs){this.value=xs[0]?.value??''},click(){}});return elements.get(id)}
const context={document:{getElementById:element,createElement:()=>({click(){}})},Option:function(text,value){this.text=text;this.value=value},Blob,URL,setTimeout};
vm.createContext(context);
const html=fs.readFileSync('dashboard/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.runInContext(script,context);
assert.equal(element('count').textContent,381);
assert.ok(Number(element('kd').textContent)>0);
assert.ok(element('chart').innerHTML.includes('<circle'));
element('team').value='G2';vm.runInContext('groupsChanged()',context);
assert.equal(element('count').textContent,478);
element('game').value='CS2';vm.runInContext('groupsChanged()',context);
assert.equal(element('count').textContent,195);
assert.equal(element('avg').textContent,'—');
element('start').value='2026-01-01';vm.runInContext('render()',context);
assert.equal(element('count').textContent,0);
assert.equal(element('kd').textContent,'—');
assert.ok(!element('maps').innerHTML.includes('NaN'));
console.log('Dashboard: default, team filter, chart and empty-state checks passed.');
