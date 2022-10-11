import { getSpans } from '../src/util/annotation.ts';

describe('A suite is just a function', function () {
  const a = [
    ['word', 'tag'],
    ['the', 'B-SUBJ'],
    ['lazy', 'I-SUBJ'],
    ['yellow', 'I-SUBJ'],
    ['socks', 'I-SUBJ'],
    ['glued', 'B-CONTRAST'],
    ['on', 'B-CONTRAST'],
    ['the', 'B-CONTRAST'],
    ['wall', 'B-CONTRAST'],
    ['.', ''],
    ['word', 'tag'],
    ['the', 'B-SUBJ'],
    ['lazy', 'I-SUBJ'],
    ['yellow', 'I-SUBJ'],
    ['socks', 'I-SUBJ'],
    ['glued', 'B-CONTRAST'],
    ['on', 'B-CONTRAST'],
    ['the', 'B-CONTRAST'],
    ['wall', 'B-CONTRAST'],
    [';', 'O'],
  ];

  it('aannotationnd so is a spec', function () {
    expect(getSpans(a)).toBe(true);
  });
});
