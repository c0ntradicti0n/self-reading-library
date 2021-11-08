export function getRandomArbitrary(min, max) {
  return Math.round(Math.random() * (max - min) + min);
}

export const zip = rows=>rows[0].map((_,c)=>rows.map(row=>row[c]))
