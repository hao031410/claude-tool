package io.terminus.tsrm.onlinemall.spi.model.test.dto;

import io.swagger.annotations.ApiModelProperty;
import io.terminus.common.api.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 测试报告(TestReport)传输模型
 *
 * @author system
 * @since 2024-01-06 16:40:00
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class TestReportDTO extends BaseModel {
    private static final long serialVersionUID = 1L;

    /**
     * @see TestReportReportFormatDict
     */
    @ApiModelProperty("报告形式。")
    private String reportFormat;

    @ApiModelProperty("报告内容")
    private String content;
}