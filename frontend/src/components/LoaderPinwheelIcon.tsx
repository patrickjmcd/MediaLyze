import { motion } from "motion/react";
import type { HTMLAttributes } from "react";

type LoaderPinwheelIconProps = HTMLAttributes<HTMLDivElement> & {
  size?: number;
};

export function LoaderPinwheelIcon({ className, size = 28, ...props }: LoaderPinwheelIconProps) {
  return (
    <div className={className} {...props}>
      <svg
        fill="none"
        height={size}
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        width={size}
        xmlns="http://www.w3.org/2000/svg"
      >
        <motion.g
          animate={{ rotate: 360 }}
          style={{ originX: "50%", originY: "50%" }}
          transition={{
            repeat: Number.POSITIVE_INFINITY,
            duration: 1,
            ease: "linear",
          }}
        >
          <path d="M22 12a1 1 0 0 1-10 0 1 1 0 0 0-10 0" />
          <path d="M7 20.7a1 1 0 1 1 5-8.7 1 1 0 1 0 5-8.6" />
          <path d="M7 3.3a1 1 0 1 1 5 8.6 1 1 0 1 0 5 8.6" />
        </motion.g>
        <circle cx="12" cy="12" r="10" />
      </svg>
    </div>
  );
}
