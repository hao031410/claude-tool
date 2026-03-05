package ${package}.app.service;

import ${package}.spi.model.dto.${entityName}DTO;
import ${package}.domain.service.${entityName}DomainService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * ${entityName}应用服务
 */
@Service
public class ${entityName}AppService {
    
    @Autowired
    private ${entityName}DomainService ${entityNameLower}DomainService;
    
    /**
     * 业务方法示例
     */
    @Transactional(rollbackFor = Exception.class)
    public void businessMethod(${entityName}DTO dto) {
        // 业务逻辑处理
    }
}
