const colors = require("@/tailwind.config").theme.extend.colors;

export const getVesselColor = (listIndex: number) => {
  const nColors = 12;
  return `vessel-color-${(listIndex - 1) % nColors + 1}`
}

/* For Tailwind
  bg-vessel-color-0
  bg-vessel-color-1
  bg-vessel-color-2
  bg-vessel-color-3
  bg-vessel-color-4
  bg-vessel-color-5
  bg-vessel-color-6
  bg-vessel-color-7
  bg-vessel-color-8
  bg-vessel-color-9
  bg-vessel-color-10
  bg-vessel-color-11
*/
export const getVesselColorBg = (listIndex: number) => {
  return `bg-${getVesselColor(listIndex)}`
}

/* For Tailwind
  text-vessel-color-0
  text-vessel-color-1
  text-vessel-color-2
  text-vessel-color-3
  text-vessel-color-4
  text-vessel-color-5
  text-vessel-color-6
  text-vessel-color-7
  text-vessel-color-8
  text-vessel-color-9
  text-vessel-color-10
  text-vessel-color-11
*/
export const getVesselColorText = (listIndex: number) => {
  return `text-${getVesselColor(listIndex)}`
}

export const getVesselColorRGB = (listIndex: number) => {
  const color = colors[`vessel-color-${listIndex}`]
  const rgb = color.replace("rgb(", "").replace(")", "").split(",")
  return rgb
}
