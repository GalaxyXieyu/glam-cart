import React, { useState, useRef, useEffect } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import FeaturedProducts from "@/components/FeaturedProducts";
import ProductDisplay from "@/components/ProductDisplay";
import Footer from "@/components/Footer";
import CartDrawer from "@/components/CartDrawer";
import FloatingActionButtons from "@/components/FloatingActionButtons";
import { Button } from "@/components/ui/button";
import { useIsMobile } from "@/hooks/use-mobile";
import { useProductFiltering } from "@/hooks/use-product-filtering";
import { useCart } from "@/hooks/use-cart";
import { useScrollDetection } from "@/hooks/use-scroll-detection";
import { useLanguage } from "@/contexts/LanguageContext";
import { useProducts, useFeaturedProducts } from "@/hooks/useProducts";

const Index = () => {
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [itemsPerPage, setItemsPerPage] = useState(8);
  const [dynamicLimit, setDynamicLimit] = useState(50); // 初始值
  const { t } = useLanguage();

  const isMobile = useIsMobile();

  // 智能计算需要获取的产品数量
  // 基于当前分页设置，我们至少需要获取前几页的数据
  const calculateOptimalLimit = (currentItemsPerPage: number) => {
    // 获取前5页的数据，确保用户有足够的浏览体验
    // 但也要考虑性能，不要一次性获取太多
    const pagesAhead = 5;
    const calculatedLimit = currentItemsPerPage * pagesAhead;
    
    // 设置合理的边界
    const minLimit = 50;
    const maxLimit = 500;
    
    return Math.max(minLimit, Math.min(maxLimit, calculatedLimit));
  };

  // 当用户改变每页显示数量时，动态调整获取的产品数量
  useEffect(() => {
    const newLimit = calculateOptimalLimit(itemsPerPage);
    if (newLimit !== dynamicLimit) {
      setDynamicLimit(newLimit);
    }
  }, [itemsPerPage]);

  // Fetch products from API - 获取所有产品
  const { data: apiProductsData, isLoading: isProductsLoading, error: productsError } = useProducts({
    enabled: true,
    limit: 1000, // 获取所有产品，设置足够大的限制
  });

  // Fetch featured products from API
  const { data: apiFeaturedProducts, isLoading: isFeaturedLoading, error: featuredError } = useFeaturedProducts(8);

  // Use API data
  const allProducts = apiProductsData?.products || [];
  const featuredProducts = apiFeaturedProducts || [];

  // 如果当前获取的产品数量接近limit，可能还有更多产品
  const mayHaveMoreProducts = allProducts.length >= dynamicLimit * 0.9;

  const { products, filters, setFilters, sortOption, setSortOption } = useProductFiltering(allProducts);
  const {
    cartItems,
    isCartOpen,
    setIsCartOpen,
    handleAddToCart,
    handleRemoveFromCart,
    handleQuantityChange,
    handleClearCart,
    totalCartItems
  } = useCart();

  // Reference for scrolling detection
  const headerRef = useRef<HTMLDivElement>(null);
  const filterRef = useRef<HTMLDivElement>(null);

  const { isFilterSticky } = useScrollDetection(headerRef);

  // Show loading state if products are loading
  if (isProductsLoading || isFeaturedLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-cosmetic-beige-100">
        <Header onCartClick={() => {}} cartItemCount={0} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cosmetic-gold-400 mx-auto mb-4"></div>
            <p className="text-cosmetic-brown-300">{t("loading") || "加载中..."}</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  // Show error state if API calls fail
  if (productsError || featuredError) {
    return (
      <div className="flex flex-col min-h-screen bg-cosmetic-beige-100">
        <Header onCartClick={() => {}} cartItemCount={0} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-cosmetic-brown-500 mb-4">加载产品时发生错误</p>
            <Button
              onClick={() => window.location.reload()}
              className="bg-cosmetic-gold-400 hover:bg-cosmetic-gold-500"
            >
              重新加载
            </Button>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-cosmetic-beige-100">
      <div ref={headerRef}>
        <Header
          onCartClick={() => setIsCartOpen(true)}
          cartItemCount={totalCartItems}
        />
        <HeroSection />
      </div>

      {/* 特色产品轮播 */}
      {!isFeaturedLoading && featuredProducts.length > 0 && (
        <FeaturedProducts products={featuredProducts} />
      )}
      
      <main className="flex-1">
        <div className="py-8" id="all-products-section">
          <div className="container mx-auto px-4 mb-6">
            <h2 className="text-2xl md:text-3xl font-serif font-bold text-cosmetic-brown-500 text-center">
              {t("allProducts")}
            </h2>
          </div>
          <ProductDisplay 
            products={products}
            filters={filters}
            sortOption={sortOption}
            onFilterChange={setFilters}
            onSortChange={setSortOption}
            onAddToCart={handleAddToCart}
            isFilterSticky={isFilterSticky}
            showMobileFilters={showMobileFilters}
            onMobileFilterClose={() => setShowMobileFilters(false)}
            isMobile={isMobile}
            filterRef={filterRef}
            itemsPerPage={itemsPerPage}
            onItemsPerPageChange={setItemsPerPage}
          />

          {/* 提示用户可能有更多产品 */}
          {mayHaveMoreProducts && (
            <div className="text-center py-4">
              <p className="text-sm text-cosmetic-brown-300">
                显示了前 {allProducts.length} 个产品。可能还有更多产品，请使用筛选功能或增加每页显示数量。
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Floating action buttons for mobile */}
      <FloatingActionButtons 
        onCartClick={() => setIsCartOpen(true)} 
        onFilterClick={() => setShowMobileFilters(true)}
        cartItemCount={totalCartItems}
      />

      <CartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cartItems={cartItems}
        onRemoveItem={handleRemoveFromCart}
        onQuantityChange={handleQuantityChange}
        onClearCart={handleClearCart}
      />

      <Footer />
    </div>
  );
};

export default Index;
