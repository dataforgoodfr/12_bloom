import React, { useEffect, useState } from "react"
import { motion, useAnimationControls } from "framer-motion"
import { ChevronUpIcon } from "lucide-react"

function ToggleHeader({
  disabled = false,
  onClick,
  children,
  className,
}: {
  disabled?: boolean
  onClick?: () => void
  children: React.ReactNode
  className?: string
}) {
  const baseClassName = disabled ? "" : "cursor-pointer"
  return (
    <div className={`${baseClassName} ${className}`} onClick={onClick}>
      {children}
    </div>
  )
}

function ToggleContent({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return <div className={className}>{children}</div>
}

export interface ToggleProps {
  disabled?: boolean
  children: React.ReactNode
  className?: string
}

function Toggle({ disabled = false, children, className }: ToggleProps) {
  const [showContent, setShowContent] = useState(false)
  const svgControls = useAnimationControls()

  useEffect(() => {
    const control = showContent ? "open" : "close"
    svgControls.start(control)
  }, [showContent, svgControls])

  const svgVariants = {
    close: {
      rotate: 360,
    },
    open: {
      rotate: 180,
    },
  }

  const onShowContent = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    if (!disabled) {
      const target = e.target as HTMLButtonElement
      if (!target.closest("button")) {
        setShowContent(!showContent)
      }
    }
  }

  const findChildren = (type: React.ElementType) => {
    return React.Children.toArray(children).find(
      (child) => React.isValidElement(child) && child.type === type
    ) as React.ReactElement | undefined
  }

  const header = findChildren(ToggleHeader)
  const content = findChildren(ToggleContent)

  const headerWithProps =
    header &&
    React.cloneElement(header, {
      onClick: onShowContent,
      disabled,
    })

  return (
    <div className={`flex gap-1 ${className}`}>
      {!disabled && (
        <div className="mt-1 flex items-start">
          <button
            className="flex rounded-full"
            onClick={() => setShowContent(!showContent)}
          >
            <motion.div
              animate={svgControls}
              variants={svgVariants}
              initial="close"
              
            >
              <ChevronUpIcon className="size-5" />
            </motion.div>
          </button>
        </div>
      )}
      <div className={`flex w-full flex-col gap-2 py-2`}>
        {headerWithProps}
        {showContent && content}
      </div>
    </div>
  )
}

export default {
  Root: Toggle,
  Header: ToggleHeader,
  Content: ToggleContent,
}
