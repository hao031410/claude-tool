package ${package}.spi.model.dto;

import io.terminus.erp.spi.model.BaseModel;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * ${entityName}DTO
 * ${description}
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class ${entityName}DTO extends BaseModel {
    
    <#list fields as field>
    /**
     * ${field.comment}
     <#if field.hasDict>
     * @see ${field.dictClass}
     </#if>
     */
    private ${field.javaType} ${field.name};
    
    </#list>
}
