// 后备筛选器选项 - 实际筛选器选项应从API获取
// Fallback filter options - actual filter options should be fetched from API
export const filterOptions = {
  tubeTypes: ["口红管", "唇釉管", "固体棒", "睫毛膏瓶", "眼线液瓶", "唇膜瓶", "粉底膏霜瓶", "发际线包材"],
  boxTypes: ["腮红盒", "粉饼高光盒", "散粉盒", "气垫盒"],
  processTypes: ["注塑", "吹瓶"],
  functionalDesigns: ["磁吸", "卡扣", "双头", "双层", "带镜子", "带刷位", "贴片", "多格"],
  shapes: ["圆形", "正方形", "长方形", "椭圆形", "波浪纹", "迷你", "儿童卡通", "不规则"],
  materials: ["AS", "PETG", "PS", "PP"],
  developmentLineMaterials: ["注塑/吹瓶", "工艺注塑", "吹瓶"],
  capacityRange: {
    min: 1,
    max: 30
  },
  compartmentRange: {
    min: 1,
    max: 20
  }
};

// 注意：前端应该优先使用从 productService.getFilterOptions() 获取的动态数据
// Note: Frontend should prioritize dynamic data from productService.getFilterOptions()
