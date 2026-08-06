import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface CardProps extends HTMLMotionProps<'div'> {
  variant?: 'glass' | 'solid' | 'gradient';
  hoverable?: boolean;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = 'glass',
  hoverable = false,
  children,
  className = '',
  ...props
}) => {
  const variants = {
    glass: 'bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-glass',
    solid: 'bg-slate-900 border border-slate-800 shadow-xl',
    gradient: 'bg-gradient-to-br from-slate-900/90 via-slate-900/50 to-indigo-950/40 border border-indigo-500/20 shadow-glass',
  };

  return (
    <motion.div
      whileHover={hoverable ? { y: -4, transition: { duration: 0.2 } } : undefined}
      className={`rounded-2xl p-6 transition-colors duration-200 ${variants[variant]} ${
        hoverable ? 'hover:border-slate-700/80 hover:shadow-2xl' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};
