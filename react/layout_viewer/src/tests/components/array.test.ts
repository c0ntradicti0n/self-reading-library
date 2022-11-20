import { indexSubsequence } from '../../helpers/array'

it('nest annotation array', () => {
  const indíces = indexSubsequence([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 7])
  expect(indíces).toEqual([4, 7])
})
