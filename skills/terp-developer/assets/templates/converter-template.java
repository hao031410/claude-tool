package ${package}.spi.convert;

import ${package}.spi.model.dto.${entityName}DTO;
import ${package}.spi.model.po.${entityName}PO;
import org.mapstruct.Mapper;

/**
 * ${entityName}转换器
 */
@Mapper(componentModel = "spring")
public interface ${entityName}Converter {
    
    ${entityName}DTO po2dto(${entityName}PO po);
    
    ${entityName}PO dto2po(${entityName}DTO dto);
    
    List<${entityName}DTO> po2dtoList(List<${entityName}PO> poList);
    
    List<${entityName}PO> dto2poList(List<${entityName}DTO> dtoList);
}
