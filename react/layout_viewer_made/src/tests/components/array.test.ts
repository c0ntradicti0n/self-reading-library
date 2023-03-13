import { indexSubsequence } from '../../helpers/array'

it('sub index array', () => {
   const indíces = indexSubsequence([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 7])
   expect(indíces).toEqual([4, 7])
})

it('sub index array multiple', () => {
   const indíces = indexSubsequence(
      [1, 2, 3, 4, 5, 6, 7, 8, 5, 6, 7],
      [5, 6, 7],
   )
   expect(indíces).toEqual([4, 7])
})

const rwObj = {
   seq: [
      'A',
      'premise',
      'is',
      'a',
      'statement',
      'that',
      'provides',
      'evidence',
      'or',
      'reasons',
      'to',
      'form',
      'a',
      'conclusion',
      ';',
      'an',
      'argument',
      'can',
      'have',
      'more',
      'than',
      'one',
      'premise',
      '.',
      'A',
      'conclusion',
      'in',
      'an',
      'argument',
      'is',
      'the',
      'main',
      'point',
      'the',
      'arguer',
      'is',
      'trying',
      'to',
      'prove',
      '.',
      'Thus',
      ',',
      'an',
      'argument',
      'has',
      'only',
      'one',
      'conclusion',
      'and',
      'one',
      'or',
      'more',
      'premises',
   ],
   subseq: [
      'A',
      'premise',
      'is',
      'a',
      'statement',
      'that',
      'provides',
      'evidence',
      'or',
      'reasons',
      'to',
      'form',
      'a',
      'conclusion',
      ';',
      'an',
      'argument',
      'can',
      'have',
      'more',
      'than',
      'one',
      'premise',
   ],
}

it('sub index array rw', () => {
   const indíces = indexSubsequence(rwObj.seq, rwObj.subseq)
   expect(indíces).toEqual([0, 23])
})
