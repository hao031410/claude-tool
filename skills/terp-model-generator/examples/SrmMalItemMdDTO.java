package io.terminus.tsrm.onlinemall.spi.model.item.dto;

import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 商品主数据表(SrmMalItemMd)传输模型
 *
 * @author system
 * @since 2024-01-06 16:30:00
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class SrmMalItemMdDTO extends BaseModel {
    private static final long serialVersionUID = -15527592597571783L;

    @ApiModelProperty("商品编码")
    private String itemCode;

    @ApiModelProperty("商品名称")
    private String itemName;

    /**
     * @see SrmMalItemMdItemTypeDict
     */
    @ApiModelProperty("商品类型")
    private String itemType;

    /**
     * @see SrmMalItemMdOnshelfStatusDict
     */
    @ApiModelProperty("上下架状态")
    private String onshelfStatus;

    /**
     * @see SrmMalItemMdApprovalStatusDict
     */
    @ApiModelProperty("审批状态")
    private String approvalStatus;

    @ApiModelProperty("供应商")
    private io.terminus.tsrm.partner.spi.model.sup.dto.SrmMdmMdVendHDTO supplier;

    @ApiModelProperty("合同行")
    private Long contractLine;

    @ApiModelProperty("物料")
    private io.terminus.erp.md.spi.model.mat.dto.GenMatMdDTO material;

    @ApiModelProperty("后台类目")
    private io.terminus.erp.md.spi.model.mat.dto.GenMatCateMdDTO category;

    @ApiModelProperty("规格")
    private String spec;

    @ApiModelProperty("型号")
    private String modelNum;

    @ApiModelProperty("单位")
    private io.terminus.erp.md.spi.model.uom.dto.GenUomTypeCfDTO unit;

    @ApiModelProperty("税率值")
    private java.math.BigDecimal taxRate;

    @ApiModelProperty("售价")
    private java.math.BigDecimal price;

    @ApiModelProperty("成本价")
    private java.math.BigDecimal costPrice;
}