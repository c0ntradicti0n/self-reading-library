import { addSpan, adjustSpanValue, spans2annotation, annotation2spans } from "../../helpers/span_tools";

const testAnnotation: [string, string][] = [
  ["the", "B-SUBJ"],
  ["lazy", "I-SUBJ"],
  ["yellow", "I-SUBJ"],
  ["socks", "L-SUBJ"],
  ["glued", "B-CONTRAST"],
  ["on", "I-CONTRAST"],
  ["the", "I-CONTRAST"],
  ["wall", "L-CONTRAST"],
  [".", "O"],
  ["the", "B-SUBJ"],
  ["lazy", "I-SUBJ"],
  ["yellow", "I-SUBJ"],
  ["socks", "L-SUBJ"],
  ["glued", "B-CONTRAST"],
  ["on", "I-CONTRAST"],
  ["the", "I-CONTRAST"],
  ["wall", "L-CONTRAST"],
  [".", ""],
];
const testSpans = annotation2spans(testAnnotation);


const testAnnotationNoSubj: [string, string][] = [
  ["the", "B-SUBJ"],
  ["lazy", "I-SUBJ"],
  ["yellow", "I-SUBJ"],
  ["socks", "I-SUBJ"],
  ["glued", "B-CONTRAST"],
  ["on", "I-CONTRAST"],
  ["the", "I-CONTRAST"],
  ["wall", "L-CONTRAST"],
  [".", "O"],
  ["lazy", "O"],
  ["yellow", "O"],
  ["socks", "O"],
  ["glued", "B-CONTRAST"],
  ["on", "I-CONTRAST"],
  ["the", "I-CONTRAST"],
  ["wall", "L-CONTRAST"],
  [".", ""],
];
const testSpansNoSubj = annotation2spans(testAnnotationNoSubj);

console.log(testSpans);

it("adjustSpan", () => {
  const result = adjustSpanValue(
    [1, 5],
    1,
    testSpans,
    2,
    "CONTRAST",
    testAnnotation
  );
  console.log(result);

});

it("annotation == span2annotation(annotation2span(annotation))", () => {
  const result = spans2annotation(testAnnotation, annotation2spans(testAnnotation))
  expect(result).toEqual(testAnnotation)

});

it("addSpan both", () => {
  const result = addSpan(testSpans, testAnnotation);
  expect(result).toHaveLength(6);
  console.log(result);
});

it("addSpan both when zero", () => {
  const result = addSpan([], testAnnotation);
  expect(result).toHaveLength(2);
  const result2 = addSpan(result, testAnnotation);
  expect(result2).toHaveLength(4);
});

it("addSpan no Subj", () => {
  const result = addSpan(testSpansNoSubj, testAnnotationNoSubj);
  expect(result).toHaveLength(4);
});
