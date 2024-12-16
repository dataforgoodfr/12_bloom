import Menu from "@mui/material/Menu"
import MenuItem from "@mui/material/MenuItem"

type ContextMenuProps = {
  setOpen: (state: boolean) => void
  open: boolean
    tooltipPosition: Record<string, number> | null
  coordinates: string
}

export default function ContextMenu({
  open,
  tooltipPosition,
    setOpen,
  coordinates
}: ContextMenuProps) {

    const copyText = (text: string) => {
        navigator.clipboard.writeText(text)
        setOpen(false)
    }

  return (
    tooltipPosition && (
      <Menu
        open={open}
        onClose={() => setOpen(false)}
        anchorReference="anchorPosition"
        anchorPosition={{
          top: tooltipPosition.top,
          left: tooltipPosition.left,
        }}
      >
        <MenuItem onClick={() => copyText(coordinates)}>Copy coordinates</MenuItem>
      </Menu>
    )
  )
}
