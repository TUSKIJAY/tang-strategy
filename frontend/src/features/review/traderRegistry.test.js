import assert from 'node:assert/strict';
import test from 'node:test';

import {
  appendTraderDraft,
  associateRegistryServerError,
  createTraderDraft,
  nextTraderSortOrder,
  normalizeTraderDraft,
  removeUnsavedTrader,
  validateTraderDraft,
} from './traderRegistry.js';

const registry = {
  schema_version: 'traders-v1',
  traders: [
    { trader_id: 'tang', display_name: 'Tang', color: '#E45756', active: true, sort_order: 10 },
    { trader_id: 'vordin', display_name: '沃德哥', color: '#4E79A7', active: true, sort_order: 20 },
  ],
};

function validDraft(overrides = {}) {
  return {
    trader_id: 'new_trader',
    display_name: 'New Trader',
    color: '#3366CC',
    active: true,
    sort_order: '30',
    ...overrides,
  };
}

test('new draft defaults only active and the next free multiple of ten', () => {
  assert.deepEqual(createTraderDraft(registry), {
    trader_id: '',
    display_name: '',
    color: '',
    active: true,
    sort_order: '30',
  });
  assert.equal(nextTraderSortOrder({ ...registry, traders: [registry.traders[0], { ...registry.traders[1], sort_order: 30 }] }), 20);
});

test('exact trader slug accepts 2 and 64 characters and rejects every frozen boundary', () => {
  const length64 = `a${'b'.repeat(63)}`;
  assert.deepEqual(validateTraderDraft(validDraft({ trader_id: 'ab' }), registry), {});
  assert.deepEqual(validateTraderDraft(validDraft({ trader_id: length64 }), registry), {});
  for (const traderId of ['a', `a${'b'.repeat(64)}`, 'New_trader', '1trader', 'new-trader']) {
    assert.match(validateTraderDraft(validDraft({ trader_id: traderId }), registry).trader_id, /2–64/);
  }
});

test('color requires a literal hash and six hex digits without rewriting', () => {
  assert.deepEqual(validateTraderDraft(validDraft({ color: '#aBc123' }), registry), {});
  for (const color of ['3366CC', '#12345', '#1234567', '#GG66CC']) {
    assert.match(validateTraderDraft(validDraft({ color }), registry).color, /六位十六进制/);
  }
  assert.equal(normalizeTraderDraft(validDraft({ color: ' 3366CC ' })).color, '3366CC');
});

test('normalization trims only surrounding whitespace and never lowercases identity', () => {
  assert.deepEqual(normalizeTraderDraft(validDraft({
    trader_id: ' New_Trader ',
    display_name: ' Display Name ',
    color: ' #ABCDEF ',
    sort_order: ' 30 ',
  })), {
    trader_id: 'New_Trader',
    display_name: 'Display Name',
    color: '#ABCDEF',
    active: true,
    sort_order: '30',
  });
  assert.match(validateTraderDraft(validDraft({ trader_id: ' New_Trader ' }), registry).trader_id, /小写/);
});

test('blank name and duplicate id, color, or order fail at the owning field', () => {
  assert.match(validateTraderDraft(validDraft({ display_name: '   ' }), registry).display_name, /不能为空/);
  assert.match(validateTraderDraft(validDraft({ trader_id: 'tang' }), registry).trader_id, /已存在/);
  assert.match(validateTraderDraft(validDraft({ color: '#e45756' }), registry).color, /不同/);
  assert.match(validateTraderDraft(validDraft({ sort_order: 20 }), registry).sort_order, /唯一/);
  assert.match(validateTraderDraft(validDraft({ sort_order: '-1' }), registry).sort_order, /非负整数/);
  assert.match(validateTraderDraft(validDraft({ sort_order: '3.5' }), registry).sort_order, /非负整数/);
});

test('append preserves the complete registry and removal affects only the unsaved row', () => {
  const appended = appendTraderDraft(registry, validDraft({ display_name: '  New Trader  ' }));
  assert.deepEqual(appended.fieldErrors, {});
  assert.equal(appended.registry.traders.length, 3);
  assert.equal(appended.registry.traders[0], registry.traders[0]);
  assert.equal(appended.registry.traders[1], registry.traders[1]);
  assert.deepEqual(appended.trader, {
    trader_id: 'new_trader',
    display_name: 'New Trader',
    color: '#3366CC',
    active: true,
    sort_order: 30,
  });
  assert.deepEqual(removeUnsavedTrader(appended.registry, 2), registry);

  const rejected = appendTraderDraft(registry, validDraft({ trader_id: 'tang' }));
  assert.equal(rejected.registry, registry);
  assert.equal(rejected.trader, null);
});

test('JSON detail and raw server paths associate only real rendered controls', () => {
  const controls = new Set([
    '0.display_name', '0.color', '0.active', '0.sort_order',
    '1.display_name', '1.color', '1.active', '1.sort_order',
    '2.trader_id', '2.display_name', '2.color', '2.active', '2.sort_order',
  ]);
  assert.deepEqual(
    associateRegistryServerError('{"detail":"registry.traders[2].color: must be unique"}', { rowCount: 3, controlPaths: controls }),
    {
      message: 'registry.traders[2].color: must be unique',
      rowIndex: 2,
      field: 'color',
      fieldPath: '2.color',
    },
  );
  assert.deepEqual(
    associateRegistryServerError('registry.traders[1].sort_order: must be unique', { rowCount: 3, controlPaths: controls }).fieldPath,
    '1.sort_order',
  );
  assert.equal(associateRegistryServerError('registry.traders[0].trader_id: immutable', { rowCount: 3, controlPaths: controls }).fieldPath, null);
  assert.equal(associateRegistryServerError('registry.traders[9].color: bad', { rowCount: 3, controlPaths: controls }).fieldPath, null);
  assert.equal(associateRegistryServerError('registry.traders[1].unknown: bad', { rowCount: 3, controlPaths: controls }).fieldPath, null);
  assert.equal(associateRegistryServerError('registry.traders: bad', { rowCount: 3, controlPaths: controls }).fieldPath, null);
  assert.equal(associateRegistryServerError('{not-json', { rowCount: 3, controlPaths: controls }).fieldPath, null);
  assert.equal(associateRegistryServerError('server unavailable', { rowCount: 3, controlPaths: controls }).fieldPath, null);
});
