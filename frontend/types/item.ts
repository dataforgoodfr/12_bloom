export type Item = {
  id: string
  title: string
  description: string
  value: string
  type: string
}

export type ItemDetails = {
  id: string
  label: string
  description: string
  relatedItemsType: string
  relatedItems: Item[]
}
