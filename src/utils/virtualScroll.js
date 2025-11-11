/**
 * Virtual Scrolling Utility for Large Lists
 * Renders only visible items for better performance
 */
import { useState, useEffect, useRef, useMemo } from 'react';

/**
 * Hook for virtual scrolling large lists
 * @param {Array} items - Full list of items
 * @param {number} itemHeight - Height of each item in pixels
 * @param {number} containerHeight - Height of scrollable container
 * @param {number} overscan - Number of items to render outside viewport (default: 3)
 */
export const useVirtualScroll = (items, itemHeight, containerHeight, overscan = 3) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);
  
  // Get visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1).map((item, index) => ({
      item,
      index: visibleRange.startIndex + index,
      offsetTop: (visibleRange.startIndex + index) * itemHeight,
    }));
  }, [items, visibleRange, itemHeight]);
  
  // Total height for scrollbar
  const totalHeight = items.length * itemHeight;
  
  // Handle scroll event
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return {
    visibleItems,
    totalHeight,
    handleScroll,
    visibleRange,
  };
};

/**
 * Virtual List Component
 * Example usage:
 * 
 * <VirtualList
 *   items={signals}
 *   itemHeight={60}
 *   height={400}
 *   renderItem={(signal) => <SignalRow signal={signal} />}
 * />
 */
export const VirtualList = ({ items, itemHeight, height, renderItem, className = '' }) => {
  const { visibleItems, totalHeight, handleScroll } = useVirtualScroll(
    items,
    itemHeight,
    height
  );
  
  return (
    <div
      className={`overflow-auto ${className}`}
      style={{ height: `${height}px` }}
      onScroll={handleScroll}
    >
      <div style={{ height: `${totalHeight}px`, position: 'relative' }}>
        {visibleItems.map(({ item, index, offsetTop }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: `${offsetTop}px`,
              height: `${itemHeight}px`,
              width: '100%',
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Hook for infinite scroll / lazy loading
 * @param {Function} loadMore - Function to load more items
 * @param {boolean} hasMore - Whether there are more items to load
 */
export const useInfiniteScroll = (loadMore, hasMore) => {
  const [isLoading, setIsLoading] = useState(false);
  const observerTarget = useRef(null);
  
  useEffect(() => {
    if (!hasMore || isLoading) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsLoading(true);
          loadMore().finally(() => setIsLoading(false));
        }
      },
      { threshold: 1.0 }
    );
    
    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }
    
    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [hasMore, isLoading, loadMore]);
  
  return { observerTarget, isLoading };
};

export default { useVirtualScroll, VirtualList, useInfiniteScroll };
