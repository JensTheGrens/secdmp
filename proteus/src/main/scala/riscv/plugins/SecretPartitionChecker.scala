package riscv.plugins

import riscv._
import spinal.core._

class SecretPartitionChecker extends Plugin[DynamicPipeline] with SecretPartitionCheckerService {
  override def setup(): Unit = {
    assert(
      pipeline.hasService[PipelineTaintService],
      "Taint tracking required for SecretPartitionChecker"
    )
    assert(
      pipeline.hasService[MemoryPartitioningService],
      "Memory partitioning required for SecretPartitionChecker"
    )

    pipeline
      .service[LsuService]
      .setAddressTranslator(new LsuAddressTranslator {
        override def translate(
            stage: Stage,
            address: UInt,
            operation: SpinalEnumCraft[LsuOperationType.type],
            width: SpinalEnumCraft[LsuAccessWidth.type]
        ): UInt = {
          pipeline
            .service[PipelineTaintService]
            .tainted(stage) := (operation === LsuOperationType.LOAD && pipeline
            .service[MemoryPartitioningService]
            .isInPartition(isStage = true, address))
          address
        }
      })
  }
}
