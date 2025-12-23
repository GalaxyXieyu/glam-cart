from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
import os
import logging
from datetime import datetime, timedelta

from database import get_db, create_tables
from models import Product, ProductImage, User, Carousel, FeaturedProduct, Settings
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    LoginRequest, TokenResponse, UserResponse, ApiResponse, ErrorResponse,
    FilterOptionsResponse, ImageUploadResponse, ProductFilters, SortOption,
    CarouselCreate, CarouselUpdate, CarouselResponse,
    FeaturedProductCreate, FeaturedProductUpdate, FeaturedProductResponse
)
from auth import (
    authenticate_user, create_access_token, get_current_active_user,
    create_admin_user, verify_token
)
from file_utils import save_multiple_files, delete_file, save_carousel_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Glam Cart Builder API",
    description="Backend API for the Glam Cart Builder application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "https://frbzhxxscekk.sealoshzh.site",
        "http://frbzhxxscekk.sealoshzh.site"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("static/images"):
    os.makedirs("static/images")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Create tables and admin user on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    db = next(get_db())
    try:
        admin_user = create_admin_user(db)
        logger.info(f"Admin user created/verified: {admin_user.username}")
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
    finally:
        db.close()

# Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = datetime.now() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time.total_seconds():.3f}s"
    )
    
    return response

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            success=False
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            success=False
        ).model_dump()
    )

# Helper functions
def convert_product_to_response(product: Product) -> dict:
    """Convert Product model to response format matching frontend expectations."""
    # Convert functional_designs from string to list
    functional_designs = []
    if product.functional_designs:
        functional_designs = [design.strip() for design in product.functional_designs.split(',') if design.strip()]
    
    return {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "description": product.description,
        "productType": product.product_type,
        "tubeType": product.tube_type,
        "boxType": product.box_type,
        "processType": product.process_type,
        "functionalDesigns": functional_designs,
        "shape": product.shape,
        "material": product.material,
        "dimensions": product.dimensions or {},
        "images": [
            {
                "id": img.id,
                "url": img.url,
                "alt": img.alt,
                "type": img.type,
                "sort_order": img.sort_order
            }
            for img in sorted(product.images, key=lambda x: x.sort_order)
        ],
        "pricing": {
            "costPrice": product.cost_price,
            "factoryPrice": product.factory_price,
            "hasSample": product.has_sample,
            "boxDimensions": product.box_dimensions,
            "boxQuantity": product.box_quantity
        },
        "inStock": product.in_stock,
        "popularityScore": product.popularity_score,
        "isFeatured": product.is_featured,
        "createdAt": product.created_at.isoformat(),
        "updatedAt": product.updated_at.isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Glam Cart Builder API", "version": "1.0.0", "docs": "/docs"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/api/auth/login", response_model=ApiResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token, expires_at = create_access_token(data={"sub": user.username})
    
    return ApiResponse(
        data={
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            },
            "expiresAt": expires_at.isoformat()
        },
        message="Login successful"
    )

@app.post("/api/auth/logout", response_model=ApiResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """Admin logout endpoint."""
    return ApiResponse(
        data=None,
        message="Logout successful"
    )

@app.get("/api/auth/verify", response_model=ApiResponse)
async def verify_token_endpoint(current_user: User = Depends(get_current_active_user)):
    """Verify JWT token endpoint."""
    return ApiResponse(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role
        },
        message="Token is valid"
    )

# Public product endpoints (no authentication required)
# Note: More specific routes must come before generic ones

@app.get("/api/products/featured", response_model=ApiResponse)
async def get_featured_products_public(
    limit: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured products for public display."""
    # Get featured products from FeaturedProduct table
    featured_products = db.query(FeaturedProduct).filter(
        FeaturedProduct.is_active == True
    ).order_by(FeaturedProduct.sort_order.asc()).limit(limit).all()

    # If no featured products, fall back to popular products
    if not featured_products:
        products = db.query(Product).filter(
            Product.in_stock == True
        ).order_by(
            Product.popularity_score.desc(),
            Product.created_at.desc()
        ).limit(limit).all()
        product_responses = [convert_product_to_response(product) for product in products]
    else:
        product_responses = [convert_product_to_response(fp.product) for fp in featured_products]

    return ApiResponse(
        data=product_responses,
        message="Featured products retrieved successfully"
    )

def split_category_values(value_list):
    """展开分隔符分割的分类值"""
    expanded_set = set()
    for item in value_list:
        if item[0]:
            values = [v.strip() for v in item[0].split('/') if v.strip()]
            expanded_set.update(values)
    return sorted(list(expanded_set))

def group_categories(items, group_mapping):
    """将分类项按组织结构分组"""
    grouped = {}
    ungrouped = []

    for item in items:
        assigned = False
        for group_name, group_items in group_mapping.items():
            if item in group_items:
                if group_name not in grouped:
                    grouped[group_name] = []
                grouped[group_name].append(item)
                assigned = True
                break

        if not assigned:
            ungrouped.append(item)

    if ungrouped:
        grouped['其他'] = ungrouped

    return grouped

@app.get("/api/products/filter-options", response_model=ApiResponse)
async def get_filter_options(db: Session = Depends(get_db)):
    """Get available filter options with improved grouping."""

    # 定义分类分组映射
    tube_groups = {
        '唇部': ['润唇管', '唇釉管', '口红管', '唇膜瓶'],
        '眼部': ['睫毛膏瓶', '睫毛膏管', '睫毛管', '睫毛膏', '眼线液瓶'],
        '面部': ['膏霜瓶', '乳液瓶', '腮红液瓶', '腮红液管'],
        '多功能': ['固体棒']
    }

    box_groups = {
        '彩妆盒': ['眼影盒', '腮红盒', '高光盒'],
        '粉类盒': ['散粉盒', '粉饼盒', '蓬蓬粉'],
        '功能盒': ['气垫盒'],
    }

    function_groups = {
        '开合方式': ['磁吸', '卡扣', '旋盖', '按压式', '挤压式'],
        '功能配件': ['带镜子', '带刷位', '带夹子', '顶片'],
        '结构特性': ['双头', '双层'],
        '外观特性': ['透明/透色', '透明/透色/实色', '透色', '儿童卡通', '挂坠款']
    }

    shape_groups = {
        '规则形状': ['圆形', '方形', '正方形', '长方形', '椭圆形'],
        '特殊形状': ['不规则', '波浪纹', '异形', '迷你']
    }

    # Get distinct values from database
    tube_types = db.query(Product.tube_type).filter(Product.tube_type.isnot(None)).distinct().all()
    box_types = db.query(Product.box_type).filter(Product.box_type.isnot(None)).distinct().all()
    shapes = db.query(Product.shape).distinct().all()
    materials = db.query(Product.material).distinct().all()
    functional_designs_query = db.query(Product.functional_designs).filter(Product.functional_designs.isnot(None)).distinct().all()

    # 展开所有分类值（支持 / 分隔的多值）
    expanded_tubes = split_category_values(tube_types)
    expanded_boxes = split_category_values(box_types)
    expanded_shapes = split_category_values(shapes)
    expanded_materials = split_category_values(materials)
    expanded_functions = split_category_values(functional_designs_query)

    # 按组织结构分组
    grouped_tubes = group_categories(expanded_tubes, tube_groups)
    grouped_boxes = group_categories(expanded_boxes, box_groups)
    grouped_functions = group_categories(expanded_functions, function_groups)
    grouped_shapes = group_categories(expanded_shapes, shape_groups)

    # Get capacity range from dimensions JSON
    capacity_min = 0
    capacity_max = 100
    try:
        products_with_capacity = db.query(Product.dimensions).filter(Product.dimensions.isnot(None)).all()
        capacities = []
        for product in products_with_capacity:
            if product[0] and isinstance(product[0], dict):
                capacity_data = product[0].get('capacity', {})
                if isinstance(capacity_data, dict):
                    if 'min' in capacity_data:
                        capacities.append(capacity_data['min'])
                    if 'max' in capacity_data:
                        capacities.append(capacity_data['max'])
        if capacities:
            capacity_min = min(capacities)
            capacity_max = max(capacities)
    except Exception as e:
        logger.warning(f"Error calculating capacity range: {e}")

    # Get compartment range from dimensions JSON
    compartment_min = 1
    compartment_max = 10
    try:
        products_with_compartments = db.query(Product.dimensions).filter(Product.dimensions.isnot(None)).all()
        compartments = []
        for product in products_with_compartments:
            if product[0] and isinstance(product[0], dict):
                compartment_count = product[0].get('compartments')
                if compartment_count:
                    compartments.append(compartment_count)
        if compartments:
            compartment_min = min(compartments)
            compartment_max = max(compartments)
    except Exception as e:
        logger.warning(f"Error calculating compartment range: {e}")

    return ApiResponse(
        data={
            "tubeTypes": grouped_tubes,
            "boxTypes": grouped_boxes,
            "functionalDesigns": grouped_functions,
            "shapes": grouped_shapes,
            "materials": expanded_materials,
            "capacityRange": {"min": capacity_min, "max": capacity_max},
            "compartmentRange": {"min": compartment_min, "max": compartment_max}
        },
        message="Filter options retrieved successfully"
    )

@app.get("/api/products", response_model=ApiResponse)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    sort: Optional[SortOption] = Query(None),
    tube_types: Optional[str] = Query(None),
    box_types: Optional[str] = Query(None),
    functional_designs: Optional[str] = Query(None),
    process_types: Optional[str] = Query(None),
    shapes: Optional[str] = Query(None),
    materials: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get products with filtering, sorting, and pagination."""
    query = db.query(Product)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.code.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )

    # Apply filters with multi-value support
    if tube_types:
        tube_type_list = tube_types.split(",")
        # Use OR conditions to match any of the selected tube types
        tube_conditions = []
        for tube_type in tube_type_list:
            tube_conditions.append(Product.tube_type.like(f"%{tube_type}%"))
        if tube_conditions:
            query = query.filter(or_(*tube_conditions))

    if box_types:
        box_type_list = box_types.split(",")
        # Use OR conditions to match any of the selected box types
        box_conditions = []
        for box_type in box_type_list:
            box_conditions.append(Product.box_type.like(f"%{box_type}%"))
        if box_conditions:
            query = query.filter(or_(*box_conditions))

    if functional_designs:
        functional_design_list = functional_designs.split(",")
        # Use OR conditions to match any of the selected functional designs
        function_conditions = []
        for design in functional_design_list:
            function_conditions.append(Product.functional_designs.like(f"%{design}%"))
        if function_conditions:
            query = query.filter(or_(*function_conditions))

    if shapes:
        shape_list = shapes.split(",")
        # Use OR conditions to match any of the selected shapes
        shape_conditions = []
        for shape in shape_list:
            shape_conditions.append(Product.shape.like(f"%{shape}%"))
        if shape_conditions:
            query = query.filter(or_(*shape_conditions))

    if materials:
        material_list = materials.split(",")
        # Use OR conditions to match any of the selected materials
        material_conditions = []
        for material in material_list:
            material_conditions.append(Product.material.like(f"%{material}%"))
        if material_conditions:
            query = query.filter(or_(*material_conditions))

    # Apply sorting
    if sort == SortOption.NEWEST:
        query = query.order_by(Product.created_at.desc())
    elif sort == SortOption.POPULAR:
        query = query.order_by(Product.popularity_score.desc())
    elif sort == SortOption.PRICE_LOW:
        query = query.order_by(Product.factory_price.asc())
    elif sort == SortOption.PRICE_HIGH:
        query = query.order_by(Product.factory_price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    # Calculate total pages
    total_pages = (total + limit - 1) // limit

    # Convert to response format
    product_responses = [convert_product_to_response(product) for product in products]

    return ApiResponse(
        data={
            "products": product_responses,
            "total": total,
            "page": page,
            "totalPages": total_pages
        },
        message="Products retrieved successfully"
    )

@app.get("/api/products/{product_id}", response_model=ApiResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ApiResponse(
        data=convert_product_to_response(product),
        message="Product retrieved successfully"
    )

# Admin product endpoints (authentication required)
@app.post("/api/products", response_model=ApiResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)."""
    # Check if product code already exists
    existing_product = db.query(Product).filter(Product.code == product_data.code).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product code already exists")

    # Create product
    product = Product(
        name=product_data.name,
        code=product_data.code,
        description=product_data.description,
        product_type=product_data.product_type,
        tube_type=product_data.tube_type,
        box_type=product_data.box_type,
        process_type=product_data.process_type,
        functional_designs=','.join(product_data.functional_designs) if product_data.functional_designs else '',
        shape=product_data.shape,
        material=product_data.material,
        dimensions=product_data.dimensions.model_dump() if product_data.dimensions else {},
        cost_price=product_data.cost_price or 0,
        factory_price=product_data.factory_price,
        has_sample=product_data.has_sample,
        box_dimensions=product_data.box_dimensions,
        box_quantity=product_data.box_quantity,
        in_stock=product_data.in_stock,
        popularity_score=product_data.popularity_score,
        is_featured=product_data.is_featured
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    # Add images if provided
    for image_data in product_data.images:
        image = ProductImage(
            product_id=product.id,
            url=image_data.url,
            alt=image_data.alt,
            type=image_data.type
        )
        db.add(image)

    db.commit()
    db.refresh(product)

    return ApiResponse(
        data=convert_product_to_response(product),
        message="Product created successfully"
    )

@app.put("/api/products/{product_id}", response_model=ApiResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if new code conflicts with existing products
    if product_data.code and product_data.code != product.code:
        existing_product = db.query(Product).filter(Product.code == product_data.code).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product code already exists")

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "dimensions" and value:
            setattr(product, field, value.model_dump() if hasattr(value, 'model_dump') else value)
        elif field == "functional_designs" and value:
            # Convert list to comma-separated string
            setattr(product, field, ','.join(value) if isinstance(value, list) else value)
        else:
            setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return ApiResponse(
        data=convert_product_to_response(product),
        message="Product updated successfully"
    )

@app.delete("/api/products/{product_id}", response_model=ApiResponse)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete associated image files
    for image in product.images:
        delete_file(image.url)  # type: ignore

    # Delete product (cascade will handle images)
    db.delete(product)
    db.commit()

    return ApiResponse(
        data=None,
        message="Product deleted successfully"
    )

@app.post("/api/products/{product_id}/images", response_model=ApiResponse)
async def upload_product_images(
    product_id: str,
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload images for a product with automatic optimization (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not images:
        raise HTTPException(status_code=400, detail="No images provided")

    # Save and optimize uploaded files
    try:
        from file_utils import save_product_images_optimized
        saved_images_info = await save_product_images_optimized(images, product.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Get current max sort_order for this product
    max_sort_order = db.query(func.max(ProductImage.sort_order)).filter(
        ProductImage.product_id == product.id
    ).scalar() or -1

    # Create image records in database
    created_images = []
    for i, img_info in enumerate(saved_images_info):
        image = ProductImage(
            product_id=product.id,
            url=img_info["url"],
            alt=img_info["alt"],
            type=img_info["type"],
            sort_order=max_sort_order + i + 1  # Append to end
        )
        db.add(image)
        created_images.append(image)

    db.commit()

    # Refresh to get IDs
    for image in created_images:
        db.refresh(image)

    return ApiResponse(
        data={
            "images": [
                {
                    "id": img.id,
                    "url": img.url,
                    "alt": img.alt,
                    "type": img.type
                }
                for img in created_images
            ]
        },
        message=f"Successfully uploaded and optimized {len(created_images)} images"
    )

@app.delete("/api/products/{product_id}/images/{image_id}", response_model=ApiResponse)
async def delete_product_image(
    product_id: str,
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a product image (admin only)."""
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file
    delete_file(image.url)  # type: ignore

    # Delete database record
    db.delete(image)
    db.commit()

    return ApiResponse(
        data=None,
        message="Image deleted successfully"
    )

@app.put("/api/products/{product_id}/images/reorder", response_model=ApiResponse)
async def reorder_product_images(
    product_id: str,
    image_orders: List[dict],  # [{"id": "image_id", "sort_order": 0}, ...]
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reorder product images (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update sort orders
    for order_data in image_orders:
        image = db.query(ProductImage).filter(
            ProductImage.id == order_data["id"],
            ProductImage.product_id == product_id
        ).first()

        if image:
            image.sort_order = order_data["sort_order"]

    db.commit()

    # Return updated images
    updated_images = db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).order_by(ProductImage.sort_order).all()

    return ApiResponse(
        data=[{
            "id": img.id,
            "url": img.url,
            "alt": img.alt,
            "type": img.type,
            "sort_order": img.sort_order
        } for img in updated_images],
        message="Images reordered successfully"
    )

# Carousel endpoints
@app.get("/api/carousels", response_model=ApiResponse)
async def get_carousels(db: Session = Depends(get_db)):
    """Get all active carousels ordered by sort_order."""
    carousels = db.query(Carousel).filter(
        Carousel.is_active == True
    ).order_by(Carousel.sort_order.asc()).all()

    carousel_responses = [
        {
            "id": carousel.id,
            "title": carousel.title,
            "description": carousel.description,
            "imageUrl": carousel.image_url,
            "linkUrl": carousel.link_url,
            "isActive": carousel.is_active,
            "sortOrder": carousel.sort_order,
            "createdAt": carousel.created_at.isoformat(),
            "updatedAt": carousel.updated_at.isoformat()
        }
        for carousel in carousels
    ]

    return ApiResponse(
        data=carousel_responses,
        message="Carousels retrieved successfully"
    )

@app.post("/api/carousels", response_model=ApiResponse)
async def create_carousel(
    title: str = Form(...),
    description: str = Form(""),
    linkUrl: str = Form(""),
    isActive: bool = Form(True),
    sortOrder: int = Form(0),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new carousel with image upload (admin only)."""
    # Save uploaded image with carousel-specific optimization
    try:
        image_url = await save_carousel_image(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save image: {str(e)}")

    carousel = Carousel(
        title=title,
        description=description,
        image_url=image_url,
        link_url=linkUrl,
        is_active=isActive,
        sort_order=sortOrder
    )

    db.add(carousel)
    db.commit()
    db.refresh(carousel)

    return ApiResponse(
        data={
            "id": carousel.id,
            "title": carousel.title,
            "description": carousel.description,
            "imageUrl": carousel.image_url,
            "linkUrl": carousel.link_url,
            "isActive": carousel.is_active,
            "sortOrder": carousel.sort_order,
            "createdAt": carousel.created_at.isoformat(),
            "updatedAt": carousel.updated_at.isoformat()
        },
        message="Carousel created successfully"
    )

@app.put("/api/carousels/{carousel_id}", response_model=ApiResponse)
async def update_carousel(
    carousel_id: str,
    title: str = Form(...),
    description: str = Form(""),
    linkUrl: str = Form(""),
    isActive: bool = Form(True),
    sortOrder: int = Form(0),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a carousel with optional image upload (admin only)."""
    carousel = db.query(Carousel).filter(Carousel.id == carousel_id).first()
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")

    # Update basic fields
    setattr(carousel, 'title', title)
    setattr(carousel, 'description', description)
    setattr(carousel, 'link_url', linkUrl)
    setattr(carousel, 'is_active', isActive)
    setattr(carousel, 'sort_order', sortOrder)

    # Handle image update if provided
    if image and image.filename:
        # Delete old image
        if carousel.image_url:
            delete_file(carousel.image_url)

        # Save new image with carousel-specific optimization
        try:
            new_image_url = await save_carousel_image(image)
            setattr(carousel, 'image_url', new_image_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to save image: {str(e)}")

    db.commit()
    db.refresh(carousel)

    return ApiResponse(
        data={
            "id": carousel.id,
            "title": carousel.title,
            "description": carousel.description,
            "imageUrl": carousel.image_url,
            "linkUrl": carousel.link_url,
            "isActive": carousel.is_active,
            "sortOrder": carousel.sort_order,
            "createdAt": carousel.created_at.isoformat(),
            "updatedAt": carousel.updated_at.isoformat()
        },
        message="Carousel updated successfully"
    )

@app.delete("/api/carousels/{carousel_id}", response_model=ApiResponse)
async def delete_carousel(
    carousel_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a carousel (admin only)."""
    carousel = db.query(Carousel).filter(Carousel.id == carousel_id).first()
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")

    # Delete associated image file
    delete_file(carousel.image_url)  # type: ignore

    # Delete carousel
    db.delete(carousel)
    db.commit()

    return ApiResponse(
        data=None,
        message="Carousel deleted successfully"
    )

# Featured Products endpoints
@app.get("/api/featured-products", response_model=ApiResponse)
async def get_featured_products_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all featured products for admin management."""
    featured_products = db.query(FeaturedProduct).filter(
        FeaturedProduct.is_active == True
    ).order_by(FeaturedProduct.sort_order.asc()).all()

    featured_responses = []
    for featured in featured_products:
        product_data = convert_product_to_response(featured.product)
        featured_responses.append({
            "id": featured.id,
            "productId": featured.product_id,
            "product": product_data,
            "isActive": featured.is_active,
            "sortOrder": featured.sort_order,
            "createdAt": featured.created_at.isoformat(),
            "updatedAt": featured.updated_at.isoformat()
        })

    return ApiResponse(
        data=featured_responses,
        message="Featured products retrieved successfully"
    )

@app.post("/api/featured-products", response_model=ApiResponse)
async def create_featured_product(
    featured_data: FeaturedProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a product to featured products (admin only)."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == featured_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if product is already featured
    existing_featured = db.query(FeaturedProduct).filter(
        FeaturedProduct.product_id == featured_data.product_id,
        FeaturedProduct.is_active == True
    ).first()
    if existing_featured:
        raise HTTPException(status_code=400, detail="Product is already featured")

    featured_product = FeaturedProduct(
        product_id=featured_data.product_id,
        is_active=featured_data.is_active,
        sort_order=featured_data.sort_order
    )

    db.add(featured_product)
    db.commit()
    db.refresh(featured_product)

    product_data = convert_product_to_response(featured_product.product)

    return ApiResponse(
        data={
            "id": featured_product.id,
            "productId": featured_product.product_id,
            "product": product_data,
            "isActive": featured_product.is_active,
            "sortOrder": featured_product.sort_order,
            "createdAt": featured_product.created_at.isoformat(),
            "updatedAt": featured_product.updated_at.isoformat()
        },
        message="Product added to featured successfully"
    )

@app.put("/api/featured-products/{featured_id}", response_model=ApiResponse)
async def update_featured_product(
    featured_id: str,
    featured_data: FeaturedProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a featured product (admin only)."""
    featured_product = db.query(FeaturedProduct).filter(FeaturedProduct.id == featured_id).first()
    if not featured_product:
        raise HTTPException(status_code=404, detail="Featured product not found")

    # Update fields
    update_data = featured_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(featured_product, field, value)

    db.commit()
    db.refresh(featured_product)

    product_data = convert_product_to_response(featured_product.product)

    return ApiResponse(
        data={
            "id": featured_product.id,
            "productId": featured_product.product_id,
            "product": product_data,
            "isActive": featured_product.is_active,
            "sortOrder": featured_product.sort_order,
            "createdAt": featured_product.created_at.isoformat(),
            "updatedAt": featured_product.updated_at.isoformat()
        },
        message="Featured product updated successfully"
    )

@app.delete("/api/featured-products/{featured_id}", response_model=ApiResponse)
async def delete_featured_product(
    featured_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a product from featured products (admin only)."""
    featured_product = db.query(FeaturedProduct).filter(FeaturedProduct.id == featured_id).first()
    if not featured_product:
        raise HTTPException(status_code=404, detail="Featured product not found")

    # Delete featured product entry
    db.delete(featured_product)
    db.commit()

    return ApiResponse(
        data=None,
        message="Product removed from featured successfully"
    )

# Settings endpoints
@app.get("/api/settings", response_model=ApiResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Get application settings."""
    settings = db.query(Settings).first()
    if not settings:
        # Create default settings if none exist
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return ApiResponse(
        data={
            "id": settings.id,
            "companyName": settings.company_name,
            "companyLogo": settings.company_logo,
            "companyDescription": settings.company_description,
            "contactPhone": settings.contact_phone,
            "contactEmail": settings.contact_email,
            "contactAddress": settings.contact_address,
            "customerServiceQrCode": settings.customer_service_qr_code,
            "wechatNumber": settings.wechat_number,
            "updatedAt": settings.updated_at.isoformat()
        },
        message="Settings retrieved successfully"
    )

@app.put("/api/settings", response_model=ApiResponse)
async def update_settings(
    company_name: str = Form(...),
    company_logo: str = Form(...),
    company_description: str = Form(...),
    contact_phone: str = Form(...),
    contact_email: str = Form(...),
    contact_address: str = Form(...),
    wechat_number: str = Form(...),
    qr_code_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update application settings (admin only)."""
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)

    # Update basic settings
    settings.company_name = company_name
    settings.company_logo = company_logo
    settings.company_description = company_description
    settings.contact_phone = contact_phone
    settings.contact_email = contact_email
    settings.contact_address = contact_address
    settings.wechat_number = wechat_number

    # Handle QR code file upload
    if qr_code_file and qr_code_file.filename:
        try:
            # Delete old QR code file if exists
            if settings.customer_service_qr_code:
                old_file_path = os.path.join("static", settings.customer_service_qr_code)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Save new QR code file
            qr_code_files = await save_multiple_files([qr_code_file], "qr_codes")
            if qr_code_files:
                settings.customer_service_qr_code = qr_code_files[0]["url"]
        except Exception as e:
            logger.error(f"Error uploading QR code: {str(e)}")
            raise HTTPException(status_code=400, detail="QR code upload failed")

    db.commit()
    db.refresh(settings)

    return ApiResponse(
        data={
            "id": settings.id,
            "companyName": settings.company_name,
            "companyLogo": settings.company_logo,
            "companyDescription": settings.company_description,
            "contactPhone": settings.contact_phone,
            "contactEmail": settings.contact_email,
            "contactAddress": settings.contact_address,
            "customerServiceQrCode": settings.customer_service_qr_code,
            "wechatNumber": settings.wechat_number,
            "updatedAt": settings.updated_at.isoformat()
        },
        message="Settings updated successfully"
    )
