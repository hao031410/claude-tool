package ${package}.adapter.admin;

import ${package}.spi.model.dto.${entityName}DTO;
import ${package}.app.service.${entityName}AppService;
import io.terminus.erp.adapter.api.Response;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import io.terminus.erp.adapter.api.Action;

/**
 * ${entityName}控制器
 */
@Action
public class ${entityName}Action {
    
    @Autowired
    private ${entityName}AppService ${entityNameLower}AppService;
    
    /**
     * REST接口示例
     */
    @PostMapping("/create")
    public Response<Void> create(@RequestBody ${entityName}DTO dto) {
        ${entityNameLower}AppService.businessMethod(dto);
        return Response.ok();
    }
}
