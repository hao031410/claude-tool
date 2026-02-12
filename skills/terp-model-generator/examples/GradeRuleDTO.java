package io.terminus.tsrm.partner.spi.model.grade.dto;

import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 等级规则表(GradeRule)传输模型
 *
 * @author system
 * @since 2024-01-06 10:00:00
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class GradeRuleDTO extends BaseModel {
    private static final long serialVersionUID = 1L;

    @ApiModelProperty("等级名称")
    private String gradeName;

    @ApiModelProperty("等级分数")
    private Integer gradeScore;

    @ApiModelProperty("等级折扣")
    private java.math.BigDecimal gradeDiscount;
}