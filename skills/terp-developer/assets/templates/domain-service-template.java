package ${package}.domain.service;

import ${package}.spi.model.dto.${entityName}DTO;
import ${package}.spi.model.po.${entityName}PO;
import ${package}.infrastructure.repo.${entityName}Repo;
import ${package}.spi.convert.${entityName}Converter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * ${entityName}领域服务
 */
@Service
public class ${entityName}DomainService {
    
    @Autowired
    private ${entityName}Repo ${entityNameLower}Repo;
    
    @Autowired
    private ${entityName}Converter ${entityNameLower}Converter;
    
    /**
     * 根据ID查询
     */
    public ${entityName}DTO findById(Long id) {
        ${entityName}PO po = ${entityNameLower}Repo.selectById(id);
        return ${entityNameLower}Converter.po2dto(po);
    }
    
    // 其他领域逻辑方法
}
