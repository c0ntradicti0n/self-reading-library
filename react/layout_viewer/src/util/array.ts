

export function getRandomArbitrary(min, max) {
  return Math.round(Math.random() * (max - min) + min);
}

export const pairwise = (array) => {
    let r= []
    for(var i=0; i < array.length - 1; i++){
        r.push([array[i], array[i + 1]])
    }
    console.log(array, r)
    return r
}
export const zip = rows=>rows[0].map((_,c)=>rows.map(row=>row[c]))
