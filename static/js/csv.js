function jsonToTsv(arr) {
  if (arr.length == 0) return '';

  const csvEscape = row => row
    .map(v => v?.toString() ?? '')
    .map(v => v.replace('"', '""'))
    .map(v => ['\t', '\n', '\r'].some(c => v.includes(c)) ? `"${v}"` : v)

  return csvEscape(Object.keys(arr[0])).join('\t') + '\r\n'
    + arr.map((v) => csvEscape(Object.values(v)).join('\t'))
      .join('\r\n')
}
