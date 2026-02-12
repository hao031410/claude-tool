package io.terminus.tsrm.onlinemall.spi.model.item.po;


import java.math.BigDecimal;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * (SrmMalItemMd)存储模型
 *
 * @author system
 * @since  2025-01-06 16:30:00
 */
@EqualsAndHashCode(callSuper = true)
@Data
@TableName(value = "srm_mal_item_md", autoResultMap = true)
public class SrmMalItemMdPO extends BaseModel {
    private static final long serialVersionUID = -83218405808155730L;

    @ApiModelProperty("编码")
    @TableField("`item_code`")
    private String itemCode;

    @ApiModelProperty("名称")
    @TableField("`item_name`")
    private String itemName;

    /**
     * @see SrmMalItemMdItemTypeDict
     */
    @ApiModelProperty("类型")
    @TableField("`item_type`")
    private String itemType;

    /**
     * @see SrmMalItemMdOnshelfStatusDict
     */
    @ApiModelProperty("上下架状态")
    @TableField("`onshelf_status`")
    private String onshelfStatus;

    /**
     * @see SrmMalItemMdApprovalStatusDict
     */
    @ApiModelProperty("审批状态")
    @TableField("`approval_status`")
    private String approvalStatus;

    @ApiModelProperty("供应商")
    @TableField("`supplier`")
    private Long supplier;

    @ApiModelProperty("合同行")
    @TableField("`contract_line`")
    private Long contractLine;

    @ApiModelProperty("物料")
    @TableField("`material`")
    private Long material;

    @ApiModelProperty("后台类目")
    @TableField("`category`")
    private Long category;

    @ApiModelProperty("规格")
    @TableField("`spec`")
    private String spec;

    @ApiModelProperty("型号")
    @TableField("`model_num`")
    private String modelNum;

    @ApiModelProperty("基本单位")
    @TableField("`unit`")
    private Long unit;

    @ApiModelProperty("税率值")
    @TableField("`tax_rate`")
    private BigDecimal taxRate;

    @ApiModelProperty("售价")
    @TableField("`price`")
    private BigDecimal price;

    @ApiModelProperty("成本价")
    @TableField("`cost_price`")
    private BigDecimal costPrice;
}