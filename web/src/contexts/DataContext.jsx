import { createContext } from 'react';

export const DataContext = createContext({
  allItems: [],
  setAllItems: () => {},
  currentItem: null,
  setCurrentItem: () => {},
  currentIndex: 0,
  setCurrentIndex: () => {},
  completedCount: 0,
  totalCount: 0,
  progressPercentage: 0
});