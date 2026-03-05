package ${package}.spi.model.po;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import io.terminus.erp.spi.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * ${entityName}PO
 * ${description}
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("${tableName}")
public class ${entityName}PO extends BaseModel {
    
    <#list fields as field>
    /**
     * ${field.comment}
     <#if field.hasDict>
     * @see ${field.dictClass}
     </#if>
     */
    @ApiModelProperty("${field.comment}")
    @TableField("`${field.columnName}`")
    private ${field.javaType} ${field.name};
    
    </#list>
}
