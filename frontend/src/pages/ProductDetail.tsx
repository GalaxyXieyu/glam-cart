import React, { useState } from "react";
import { useParams } from "react-router-dom";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import CartDrawer from "@/components/CartDrawer";
import { Button } from "@/components/ui/button";
import {
  ShoppingCart,
  ChevronRight,
  Heart,
  Share,
  ImageIcon
} from "lucide-react";
import { CosmeticProduct } from "@/types/cosmetics";
import { useToast } from "@/hooks/use-toast";
import { useLanguage } from "@/contexts/LanguageContext";
import { useProduct } from "@/hooks/useProducts";
import { useCart } from "@/hooks/use-cart";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import OptimizedImage from "@/components/OptimizedImage";
import ImageViewer from "@/components/ImageViewer";
import { getAllImagesInfo, getOptimizedImageProps } from "@/utils/productImageHelpers";

const ProductDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [selectedImageIndex, setSelectedImageIndex] = useState<number>(0);
  const [isImageViewerOpen, setIsImageViewerOpen] = useState<boolean>(false);
  const { toast } = useToast();
  const { t } = useLanguage();
  
  // 使用购物车hook
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

  // Fetch product from API
  const { data: product, isLoading, error } = useProduct(id || '', !!id);

  // Get optimized image info
  const allImagesInfo = product ? getAllImagesInfo(product) : [];
  const selectedImageInfo = allImagesInfo[selectedImageIndex];

  // Reset selected image when product changes
  React.useEffect(() => {
    if (product && allImagesInfo.length > 0) {
      setSelectedImageIndex(0);
    }
  }, [product, allImagesInfo.length]);

  // Show error toast if API call fails
  React.useEffect(() => {
    if (error) {
      toast({
        title: "加载失败",
        description: "获取产品信息时发生错误",
        variant: "destructive",
      });
    }
  }, [error, toast]);

  const handleAddToCartAndInquiry = () => {
    if (product) {
      // 添加商品到购物车
      handleAddToCart(product);
      // 打开购物车侧边栏
      setIsCartOpen(true);
      toast({
        title: t("addToCartInquiry"),
        description: `${product.name} ${t("addedToCartAndInquiry")}`,
      });
    }
  };

  // 处理购物车点击
  const handleCartClick = () => {
    setIsCartOpen(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-cosmetic-beige-100 flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-12 flex justify-center items-center">
          <p className="text-cosmetic-brown-300">加载中...</p>
        </main>
        <Footer />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-cosmetic-beige-100 flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-12 flex justify-center items-center">
          <p className="text-cosmetic-brown-300">产品未找到</p>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cosmetic-beige-100 flex flex-col">
      <Header 
        onCartClick={handleCartClick}
        cartItemCount={totalCartItems}
      />
      <main className="flex-1 container mx-auto px-4 py-12">
        {/* Breadcrumb */}
        <div className="text-sm text-cosmetic-brown-300 mb-6 flex items-center">
          <a href="/" className="hover:text-cosmetic-brown-500">首页</a>
          <ChevronRight className="h-4 w-4 mx-2" />
          <span>{product.tubeType || product.boxType}</span>
          <ChevronRight className="h-4 w-4 mx-2" />
          <span className="text-cosmetic-brown-500">{product.name}</span>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Product Images */}
            <div>
              <div
                className="mb-4 aspect-square overflow-hidden rounded-lg bg-cosmetic-beige-100 flex items-center justify-center cursor-pointer hover:bg-cosmetic-beige-200 transition-colors group"
                onClick={() => selectedImageInfo && setIsImageViewerOpen(true)}
              >
                {selectedImageInfo ? (
                  <div className="w-full h-full relative">
                    <OptimizedImage
                      productCode={selectedImageInfo.productCode}
                      imageName={selectedImageInfo.imageName}
                      alt={product.name}
                      usage="detail-main"
                      className="group-hover:scale-105 transition-transform duration-300"
                      lazy={false}
                      priority={true}
                    />
                    {/* 点击提示 */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
                      <div className="bg-white/90 text-cosmetic-brown-600 px-3 py-1 rounded-full text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        点击查看大图
                      </div>
                    </div>
                  </div>
                ) : (
                  <ImageIcon className="h-16 w-16 text-cosmetic-beige-300" />
                )}
              </div>
              <div className="grid grid-cols-5 gap-2">
                {allImagesInfo.map((imageInfo, index) => (
                  <div
                    key={index}
                    className={`aspect-square rounded overflow-hidden cursor-pointer border-2 ${
                      selectedImageIndex === index ? 'border-cosmetic-gold-400' : 'border-transparent'
                    }`}
                    onClick={() => setSelectedImageIndex(index)}
                  >
                    <div className="w-full h-full">
                      <OptimizedImage
                        productCode={imageInfo.productCode}
                        imageName={imageInfo.imageName}
                        alt={`${product.name} - ${index + 1}`}
                        usage="gallery-thumbnail"
                        className=""
                        lazy={true}
                        priority={false}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Product Info */}
            <div>
              <h1 className="text-2xl md:text-3xl font-serif font-semibold mb-2 gold-text">
                {product.name}
              </h1>
              <p className="text-cosmetic-brown-300 mb-6">{t("code")}: {product.code}</p>

              <div className="space-y-6 mb-6">
                {/* 关键信息：长宽高材质 - 2x2 网格 */}
                <div className="grid grid-cols-2 gap-6">
                  {product.dimensions.length && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-2">长度</p>
                      <p className="text-xl font-semibold text-cosmetic-brown-300">{product.dimensions.length}mm</p>
                    </div>
                  )}
                  {product.dimensions.width && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-2">宽度</p>
                      <p className="text-xl font-semibold text-cosmetic-brown-300">{product.dimensions.width}mm</p>
                    </div>
                  )}
                  {product.dimensions.height && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-2">高度</p>
                      <p className="text-xl font-semibold text-cosmetic-brown-300">{product.dimensions.height}mm</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium text-cosmetic-brown-500 mb-2">{t("material")}</p>
                    <p className="text-xl font-semibold text-cosmetic-brown-300">{product.material}</p>
                  </div>
                </div>

                {/* 其他信息 - 每行3个，包含容量和内格数 */}
                <div className="grid grid-cols-3 gap-4">
                  {product.dimensions.capacity && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">容量</p>
                      <p className="text-base font-medium text-cosmetic-brown-300">{product.dimensions.capacity.min}-{product.dimensions.capacity.max}ml</p>
                    </div>
                  )}
                  {product.dimensions.compartments && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">内格数</p>
                      <p className="text-base font-medium text-cosmetic-brown-300">{product.dimensions.compartments}格</p>
                    </div>
                  )}
                  {product.dimensions.weight && (
                    <div>
                      <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">重量</p>
                      <p className="text-base font-medium text-cosmetic-brown-300">{product.dimensions.weight}g</p>
                    </div>
                  )}
                </div>

                {/* 第二行次要信息 */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">{t("shape")}</p>
                    <p className="text-base text-cosmetic-brown-300">{product.shape}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">{t("type")}</p>
                    <p className="text-base text-cosmetic-brown-300">{product.tubeType || product.boxType}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-cosmetic-brown-500 mb-1">工艺</p>
                    <p className="text-base text-cosmetic-brown-300">{product.processType}</p>
                  </div>
                </div>

                {/* 功能设计 - 独立区域 */}
                <div>
                  <p className="text-sm font-medium text-cosmetic-brown-500 mb-3">功能设计</p>
                  <div className="flex flex-wrap gap-2">
                    {(() => {
                      // 处理functionalDesigns可能是字符串或数组的情况
                      const designs = Array.isArray(product.functionalDesigns) 
                        ? product.functionalDesigns 
                        : product.functionalDesigns ? [product.functionalDesigns] : [];
                      
                      return designs.map((design, index) => (
                      <span 
                        key={index} 
                        className="px-3 py-1.5 bg-cosmetic-beige-100 text-cosmetic-brown-400 rounded-full text-sm"
                      >
                        {design}
                      </span>
                      ));
                    })()}
                  </div>
                </div>
              </div>

              <div className="bg-cosmetic-beige-50 p-4 rounded-lg mb-6">
                <div className="flex items-center text-cosmetic-brown-400">
                  <span className="text-sm">{t("priceInquiryNote")}</span>
                </div>
              </div>

              <div className="mb-6">
                <Button 
                  className="w-full bg-cosmetic-gold-400 hover:bg-cosmetic-gold-500 text-white py-3 text-lg"
                  onClick={handleAddToCartAndInquiry}
                >
                  <ShoppingCart className="mr-2 h-5 w-5" />
                  {t("addToCartInquiry")}
                </Button>
              </div>

              <div className="flex items-center gap-4">
                <Button variant="ghost" className="text-cosmetic-brown-300 hover:text-cosmetic-brown-500">
                  <Share className="h-4 w-4 mr-2" />
                  分享
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Specifications Only */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div>
            <h2 className="text-xl font-serif font-semibold mb-4 gold-text">详细规格与尺寸图</h2>
            
            {/* 如果有尺寸图片，优先显示 */}
            <div className="mb-6">
              {product.images.filter(img => img.type === 'dimensions').map((image) => (
                <div key={image.id} className="rounded-lg overflow-hidden mb-4">
                  <img 
                    src={image.url} 
                    alt="产品尺寸图"
                    className="w-full h-auto" 
                  />
                </div>
              ))}
            </div>

            {/* 补充完整的规格表格（如果需要） */}
            {(product.dimensions.weight || product.dimensions.length || product.dimensions.width || product.dimensions.height) && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>详细参数</TableHead>
                    <TableHead>规格</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {product.dimensions.weight && (
                    <TableRow>
                      <TableCell className="font-medium">重量</TableCell>
                      <TableCell>{product.dimensions.weight}g</TableCell>
                    </TableRow>
                  )}
                  {product.dimensions.length && (
                    <TableRow>
                      <TableCell className="font-medium">长度</TableCell>
                      <TableCell>{product.dimensions.length}mm</TableCell>
                    </TableRow>
                  )}
                  {product.dimensions.width && (
                    <TableRow>
                      <TableCell className="font-medium">宽度</TableCell>
                      <TableCell>{product.dimensions.width}mm</TableCell>
                    </TableRow>
                  )}
                  {product.dimensions.height && (
                    <TableRow>
                      <TableCell className="font-medium">高度</TableCell>
                      <TableCell>{product.dimensions.height}mm</TableCell>
                    </TableRow>
                  )}
                  {product.dimensions.capacity && (
                    <TableRow>
                      <TableCell className="font-medium">容量范围</TableCell>
                      <TableCell>{product.dimensions.capacity.min}-{product.dimensions.capacity.max}ml</TableCell>
                    </TableRow>
                  )}
                  {product.dimensions.compartments && (
                    <TableRow>
                      <TableCell className="font-medium">内格数</TableCell>
                      <TableCell>{product.dimensions.compartments}格</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </div>
        </div>
      </main>
      <Footer />
      
      {/* 购物车侧边栏 */}
      <CartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cartItems={cartItems}
        onRemoveItem={handleRemoveFromCart}
        onQuantityChange={handleQuantityChange}
        onClearCart={handleClearCart}
      />

      {/* 图片查看器 */}
      <ImageViewer
        isOpen={isImageViewerOpen}
        onClose={() => setIsImageViewerOpen(false)}
        images={allImagesInfo}
        initialIndex={selectedImageIndex}
        productName={product?.name || ''}
      />
    </div>
  );
};

export default ProductDetail;
