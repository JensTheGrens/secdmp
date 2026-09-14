package riscv.plugins

import riscv._
import spinal.core._
import spinal.lib._

class SecurityController(securityCsrId: Int = 0x70b)(implicit config: Config)
    extends Plugin[Pipeline]
    with SecurityService {
  private var securityCsrIo: CsrIo = null

  private def convertToSecurityMode(value: UInt): SpinalEnumCraft[SecurityModeType.type] = {
    val mode = SecurityModeType()
    switch(value) {
      is(0) {
        mode := SecurityModeType.OFF
      }
      is(1) {
        mode := SecurityModeType.MEDIUM
      }
      default {
        mode := SecurityModeType.HIGH
      }
    }
    mode
  }

  private class securityCsr(implicit config: Config) extends Csr {
    val securityMode = RegInit(SecurityModeType.OFF)
    override def read(): UInt = securityMode.asBits.asUInt.resize(config.isa.xlen bits)
    override def write(mode: UInt): Unit = {
      securityMode := convertToSecurityMode(mode)
    }
  }

  override def setup(): Unit = {
    pipeline plug new Area {
      pipeline.service[CsrService].registerCsr(securityCsrId, new securityCsr)
    }
  }

  override def getSecurityMode(isStage: Boolean): SpinalEnumCraft[SecurityModeType.type] = {
    if (isStage) { // build a new CsrIo
      def readOnlyCsr(csrId: Int): CsrIo = {
        val csrIn = slave(new CsrIo)
        pipeline plug new Area {
          csrIn <> pipeline.service[CsrService].getCsr(csrId)
        }
        csrIn.wdata.assignDontCare()
        csrIn.write := False
        csrIn
      }
      val newSecurityCsrIo = readOnlyCsr(securityCsrId)
      convertToSecurityMode(newSecurityCsrIo.read())
    } else {
      if (securityCsrIo == null) {
        pipeline plug new Area {
          def readOnlyCsr(csrId: Int): CsrIo = {
            val csr = pipeline.service[CsrService].getCsr(csrId)
            csr.wdata.assignDontCare()
            csr.write := False
            csr
          }
          securityCsrIo = readOnlyCsr(securityCsrId)
        }
      }
      // use the securityCsrIo plugged into `pipeline`
      convertToSecurityMode(securityCsrIo.read())
    }
  }
}
