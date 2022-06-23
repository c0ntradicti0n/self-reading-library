import {nest} from "./array.js";

export const tagStrip = (t) => {
    if (t.length<2)
        return ""
    return t.slice(2)
}

export const getSpans = (annotation)  => {
    let groups :  [string, number, number, string[]][] = annotation.reduce((acc, [w, t], i) => {
        if (acc.length === 0)
            return [[tagStrip(t), 0, i+1, [w]]]
        let last = acc[acc.length -1]
        console.log(last)
        if (last[0] === tagStrip(t))
            acc[acc.length - 1] = [tagStrip(t), last[1], i+1, [...last[3], w]]
        else
            acc.push([tagStrip(t), i, i + 1, [ w]])
        return acc
    }, [])
    console.log(groups)
    groups = groups.filter(([t, i1, i2]) => t.length > 2);
    return groups
}

