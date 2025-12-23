
// 管型类型现在接受任意字符串，不再限制预定义类型
export type TubeType = string;

// 盒型类型现在接受任意字符串，不再限制预定义类型
export type BoxType = string;

// 功能设计现在接受任意字符串，不再限制预定义类型
export type FunctionalDesign = string;

// 形状类型现在接受任意字符串，不再限制预定义类型
export type Shape = string;

// 材质类型现在接受任意字符串，不再限制预定义类型
export type Material = string;

// 开发线材质现在接受任意字符串，不再限制预定义类型
export type DevelopmentLineMaterial = string;

// 工艺类型现在接受任意字符串，不再限制预定义类型
export type ProcessType = string;

export interface ProductDimensions {
  weight?: number;  // in grams
  length?: number;  // in mm
  width?: number;   // in mm
  height?: number;  // in mm
  capacity?: {
    min: number;
    max: number;
  };
  compartments?: number;
}

export interface ProductImage {
  id: string;
  url: string;
  alt: string;
  type: 'main' | 'gallery' | 'dimensions' | 'detail';
  sort_order: number;
}

export interface ProductPricing {
  hasSample: boolean;
  boxDimensions?: string;
  boxQuantity?: number;
}

export interface CosmeticProduct {
  id: string;
  name: string;
  code: string;
  description: string;
  tube_type?: TubeType;
  box_type?: BoxType;
  process_type?: ProcessType;
  functional_designs: FunctionalDesign[] | string;
  shape: Shape;
  material: Material;
  development_line_materials?: DevelopmentLineMaterial[];
  dimensions: ProductDimensions;
  images: ProductImage[];
  pricing: ProductPricing;
  in_stock: boolean;
  popularity_score: number;
  created_at: string;
  updated_at: string;
}

export interface FilterOptions {
  tubeTypes?: TubeType[];
  boxTypes?: BoxType[];
  functionalDesigns?: FunctionalDesign[];
  shapes?: Shape[];
  materials?: Material[];
  developmentLineMaterials?: DevelopmentLineMaterial[];
  capacityRange?: {
    min: number;
    max: number;
  };
  compartmentRange?: {
    min: number;
    max: number;
  };
  searchText?: string;
}

export type SortOption = 'newest' | 'popular';

export interface CartItem {
  product: CosmeticProduct;
  quantity: number;
}

export interface ImageUpload {
  file: File;
  preview: string;
  id: string;
}

export interface OrderIntent {
  items: CartItem[];
  totalPrice: number;
  date: string;
  orderId: string;
}
