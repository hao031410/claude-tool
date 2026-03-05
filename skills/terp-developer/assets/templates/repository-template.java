package ${package}.infrastructure.repo;

import ${package}.spi.model.po.${entityName}PO;
import io.terminus.erp.infrastructure.repo.BaseRepository;
import org.springframework.stereotype.Repository;

/**
 * ${entityName}仓库
 */
@Repository
public interface ${entityName}Repo extends BaseRepository<${entityName}PO> {
    
    // 自定义查询方法示例：
    // default List<${entityName}PO> findByStatus(String status) {
    //     return selectList(new LambdaQueryWrapper<${entityName}PO>()
    //         .eq(${entityName}PO::getStatus, status));
    // }
}
