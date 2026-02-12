package io.terminus.tsrm.partner.spi.model.grade.po;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 等级规则表(GradeRule)存储模型
 *
 * @author system
 * @since 2024-01-06 10:00:00
 */
@EqualsAndHashCode(callSuper = true)
@Data
@TableName("grade_rule")
public class GradeRulePO extends BaseModel {
    private static final long serialVersionUID = 1L;

    @ApiModelProperty("等级名称")
    @TableField("`grade_name`")
    private String gradeName;

    @ApiModelProperty("等级分数")
    @TableField("`grade_score`")
    private Integer gradeScore;

    @ApiModelProperty("等级折扣")
    @TableField("`grade_discount`")
    private java.math.BigDecimal gradeDiscount;
}